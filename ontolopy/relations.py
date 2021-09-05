import logging
import numpy as np
import pandas as pd
import re

# divide between term (r) and relation (r) in relation path
divider_tr = '.'
divider_rt = '~'


def _tuple_list_to_dict(tuple_list):
    tuple_dict = {}
    for k, v in tuple_list:
        try:
            tuple_dict[k].append(v)
        except KeyError:
            tuple_dict[k] = [v]
    return tuple_dict


def relation_path_to_text(relation_path, ont):
    """
    Converts from a relation string e.g. "UBERON:123913.is_a~UBERON:1381239" to a text version,
     e.g. "heart is a circulatory organ".

    :param ont: opy.Obo() ontology object.
    :param relation_path: path describing the relationship between two terms, e.g. "UBERON:123913.is_a-UBERON:1381239"
    :return:
    """
    if pd.isna(relation_path):
        return relation_path
    # TODO: add fix for alt-ids, obsolete terms, etc. For now just keep their ID.
    for i, sub_relation in enumerate(relation_path.split(divider_tr)):
        if i == 0:
            # sub_relation is actually the source *term* identifier for i == 0.
            try:
                relation_text = ont[sub_relation]['name']
            except KeyError:
                relation_text = sub_relation
            continue
        relation = sub_relation.split(divider_rt)[0].replace('_', ' ')
        term_id = sub_relation.split(divider_rt)[-1]
        try:
            relation_text += f" {relation} {ont[term_id]['name']}"
        except KeyError:
            relation_text += f" {relation} {term_id}"
    return relation_text


def _found_term(relation_path):
    """
    Finds the last term in the relation path.

    :param relation_path:
    :return:
    """

    if pd.isna(relation_path):
        return relation_path
    else:
        return relation_path.split(divider_rt)[-1]


def _check_if_found(new_term: str, targets: list) -> bool:
    """
    Checks if `new_term` matches `targets`.

    :param new_term: string to check
    :param targets: list of strings to match to `new_term`. Targets can be a list of specific targets, e.g.
        ['UBERON:123219', 'UBERON:1288990'] or of general ontology prefixes, e.g. ['UBERON']
    :return:
    """

    if (':' in targets[0]) and (new_term in targets):  # specific
        relation_found = True
    elif (':' not in targets[0]) and (new_term.split(':')[0] in targets):  # general
        relation_found = True
    else:
        relation_found = False

    return relation_found


class Relations(pd.DataFrame):

    def __init__(self, allowed_relations: list, ont, sources=None, targets=None, source_targets=None, excluded=None, col_names=None, mode='any'):
        """
        Pandas Dataframe containing relationships between `sources` and `targets` terms according to `ont`.
        Finds relationships that do not pass through `excluded` terms and uses only `allowed_relations`. We keep looking
        until we find a relation to a target (if mode == 'any') or we run out of leads.

        :param allowed_relations: a list of allowed relations, e.g. ['is_a', 'part_of']
        :param sources: list of sources. For mode `all` must be a list of source-target tuple airs.
        :param mode: 'any' or 'all' - 'all is looking for specific term1-term2 pairs, while 'any' is looking for any
          relationship between something in specific source and anything in targets.
        :param targets: list of targets.
        :param source_targets: list of tuples of source-target pairs. Do not provide source or targets if using this
          parameter. Only runs in "all" mode.
        :param ont: Obo ontology object.
        :param excluded: a list/set of terms which are explicitly not being searched for (which may otherwise match the
          targets). Useful e.g. if we want to look for any tissue targets with prefix 'UBERON', except for very general
          ones. Does not allow relationships that pass through this term.
        :param col_names: Alternative column names for the output of Relations Data Frame, by default is
          ['from', 'relation_path', 'relation_text', 'to']
        """
        # TODO: Add default for allowed_relations?
        # TODO: put parameters in order

        assert (mode in ['any', 'all'])

        if source_targets:
            assert mode == 'all'
            assert (not sources)
            assert (not targets)
            assert (not excluded)
        else:
            assert targets
            assert isinstance(targets, list)

        if col_names is None:
            col_names = ['from', 'relation_path', 'relation_text', 'to']
        else:
            assert len(col_names) == 4

        if excluded is None:
            excluded = []

        assert(isinstance(allowed_relations, list))

        if not isinstance(sources, type(None)):
            if mode == 'any':
                assert sources.__iter__

        # TODO: remove/test source_targets.
        #
        #     else:
        #         source_targets = zip(sources, targets)
        #
        # if source_targets:
        #     assert source_targets.__iter__
        #     row_index = source_targets

        super(Relations, self).__init__(data=None,
                                        index=sources,
                                        columns=col_names[1:],
                                        dtype=None,
                                        copy=True)
        self.index.rename(col_names[0], inplace=True)

        if mode == 'any':
            self._calculate_any(allowed_relations, targets, ont, excluded)
        elif mode == 'all':
            # TODO: fix/test for both source-target and source-and-target modes
            self._calculate_all(allowed_relations, targets, ont, excluded)

    def _calculate_all(self, allowed_relations, targets, ont, excluded):
        """
        Looks for relations between all specified pairs of source term to target term.

        Basically, only stops looking when we stop getting new relations.

        :param allowed_relations:
        :param ont:
        :param excluded:
        :return:
        """
        # TODO: Add functionaltiy for source_targets, or remove because this function is the same as _calculate_any
        found_relation_paths = []
        for source in self.index:
            found_relation_path_list = _find_relation(source, allowed_relations, targets, ont, excluded, 'all')
            found_relation_paths.append(found_relation_path_list)

        # Format output:
        self.iloc[:, 0] = found_relation_paths
        self.iloc[:, 1] = [[relation_path_to_text(pth, ont) for pth in lst] for lst in found_relation_paths]
        self.iloc[:, 2] = [[_found_term(pth) for pth in lst] for lst in found_relation_paths]

    def _calculate_any(self, allowed_relations, targets, ont, excluded):
        """
        Looks for relation of any souce term to any target term. Stops looking when relation found.

        :param allowed_relations:
        :param targets:
        :param ont:
        :param excluded:
        :return:
        """
        found_relation_paths = []
        for source in self.index:
            # TODO: Make sure that _check_if_found can handle both types of target
            found_relation_path = _find_relation(source, allowed_relations, targets, ont, excluded)
            found_relation_paths.append(found_relation_path)

            # Format output:
        self.iloc[:, 0] = found_relation_paths
        self.iloc[:, 1] = [relation_path_to_text(relation_path, ont) for relation_path in found_relation_paths]
        self.iloc[:, 2] = [_found_term(relation_path) for relation_path in found_relation_paths]

    def format_all(self, ont, targets):
        """
        Creates a nicely formatted multi-indexed DataFrame with (source, target) pairs. Useful when using "mode=all".

        :param ont: ontology to look up paths.
        :param targets: list of term IDs, e.g. ['GO', 'UBERON']
        :return:
        """
        # Get all source-target pairs (keys) and relation paths/strings (list as values)
        source_target_dict = {}
        for tissue_term, row in self.iterrows():
            for i, relation_path in enumerate(row['relation_path']):
                for target in targets:
                    for go_term in re.findall(f'({target}:\d+)', relation_path):
                        relation_path_target = relation_path.split(go_term)[0] + go_term
                        relation_text_target = relation_path_to_text(relation_path_target, ont)
                        source_target_dict[(tissue_term, go_term)] = [relation_path_target, relation_text_target]

        # Format into a multi-indexed data frame:
        formatted_df = pd.DataFrame.from_dict(source_target_dict,
                                              orient='index',
                                              columns=['relation_path', 'relation_text'])
        formatted_df.index = pd.MultiIndex.from_tuples(formatted_df.index, names=["from", "to"])

        return formatted_df


def _find_relation(source, allowed_relations, targets, ont, excluded, mode='any'):
    """
    Searches ontology `ont` for a relationship path between `source` and `target` (self.index), which does not pass
    through `excluded` and uses only `allowed_relations`.

    We keep looking until we find a relation to a target (relation_found == True) or we run out of leads
    (unchanged == True, i.e. we have no new relation strings after another loop).

    :param allowed_relations:
    :param targets: list of types of targets, e.g. ["GO"]
    :param ont:
    :param excluded:
    :return:
    """
    # TODO: check if it's quicker to have a list of tuples ('is_a', 'termID') instead of long string.
    #
    if mode == 'all':
        found_relation_paths = set()

    checked_terms = set()

    relation_paths = [source]
    relation_found = False
    unchanged = False

    while (not (relation_found and mode == 'any')) and (not unchanged):
        new_relation_paths = []
        for relation_path in relation_paths:
            most_recent_term = relation_path.split(divider_rt)[-1]

            if most_recent_term in checked_terms:
                continue
            else:
                checked_terms.add(most_recent_term)

            # Ontologies can contain external terms, e.g. `NCBITaxon:9606`
            try:
                relations = ont[most_recent_term].keys()
            except KeyError:
                relations = []

            for relation in relations:
                if relation not in allowed_relations:
                    new_terms = []
                else:
                    new_terms = ont[most_recent_term][relation]

                # For each new term, check for wanted relation:
                for new_term in new_terms:

                    if new_term in excluded:
                        continue

                    if new_term in relation_path:
                        logging.info(f'cyclic relationship: '
                                     f'{relation_path}{divider_tr}{relation}{divider_rt}{new_term}')
                        continue

                    new_relation_path = f'{relation_path}{divider_tr}{relation}{divider_rt}{new_term}'
                    new_relation_paths.append(new_relation_path)

                    relation_found = _check_if_found(new_term, targets)
                    if relation_found and mode == 'all':
                        found_relation_paths.add(new_relation_path)
                    elif relation_found and mode == 'any':
                        return new_relation_path

        if len(new_relation_paths) == 0:
            unchanged = True
        relation_paths = new_relation_paths

    if mode == 'any':
        return np.nan
    if mode == 'all':
        return found_relation_paths

