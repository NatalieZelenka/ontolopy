import logging
import numpy as np
import pandas as pd

# divide between term (r) and relation (r) in relation path
divider_tr = '.'
divider_rt = '~'


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

    for i, sub_relation in enumerate(relation_path.split(divider_tr)):
        if i == 0:
            # sub_relation is actually the source *term* identifier for i == 0.
            relation_text = ont[sub_relation]['name']
            continue
        relation = sub_relation.split(divider_rt)[0].replace('_', ' ')
        term_id = sub_relation.split(divider_rt)[-1]

        relation_text += f" {relation} {ont[term_id]['name']}"
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

    def __init__(self, allowed_relations: list, sources: list, targets: list, ont, excluded=None, col_names=None):
        """
        Pandas Dataframe containing relationships between `sources` and `targets` terms according to `ont`.

        Finds relationships that do not pass through `excluded` terms and uses only `allowed_relations`. We keep looking
         until we find a relation to a target or we run out of leads.

        :param allowed_relations:
        :param sources:
        :param targets:
        :param ont:
        :param excluded:
        :param col_names:
        """

        if col_names is None:
            col_names = ['from', 'relation_path', 'relation_text', 'to']
        else:
            assert(len(col_names) == 4)

        if excluded is None:
            excluded = []

        assert(isinstance(targets, list))
        assert(isinstance(allowed_relations, list))
        assert(sources.__iter__)

        super(Relations, self).__init__(data=None,
                                        index=sources,
                                        columns=col_names[1:],
                                        dtype=None,
                                        copy=True)
        self.index.rename(col_names[0], inplace=True)
        self._calculate(allowed_relations, targets, ont, excluded)

    def _calculate(self, allowed_relations, targets, ont, excluded):
        """
        Searches ontology `ont` for a relationship path between `source` and `target` (self.index), which does not pass
        through `excluded` and uses only `allowed_relations`.

        We keep looking until we find a relation to a target (relation_found == True) or we run out of leads
        (unchanged == True, i.e. we have no new relation strings after another loop).

        :param allowed_relations:
        :param targets:
        :param ont:
        :param excluded:
        :return:
        """

        # TODO: try to vectorise
        found_relation_paths = []
        for source in self.index:
            relation_paths = [source]

            relation_found = False
            unchanged = False

            while (not relation_found) and (not unchanged):

                new_relation_paths = []
                for relation_path in relation_paths:
                    most_recent_term = relation_path.split(divider_rt)[-1]

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

                            new_relation_path = relation_path + divider_tr + relation + divider_rt + new_term
                            new_relation_paths.append(new_relation_path)

                            relation_found = _check_if_found(new_term, targets)
                            if relation_found:
                                break

                        if relation_found:
                            break
                    if relation_found:
                        break

                if len(new_relation_paths) == 0:
                    unchanged = True
                relation_paths = new_relation_paths

            if relation_found:
                found_relation_paths.append(new_relation_path)
            else:
                found_relation_paths.append(np.nan)

        # Format output:
        self.iloc[:, 0] = found_relation_paths
        self.iloc[:, 1] = [relation_path_to_text(relation_path, ont) for relation_path in found_relation_paths]
        self.iloc[:, 2] = [_found_term(relation_path) for relation_path in found_relation_paths]

        return self
