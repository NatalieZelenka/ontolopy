import time
import logging
import numpy as np
import pandas as pd


def relation_string_to_text(ont, relation_string):
    """
    Converts from a relation string e.g. "UBERON:123913.is_a_UBERON:1381239" to a text version,
     e.g. "heart is a circulatory organ".
    :param ont:
    :param relation_string:
    :return:
    """
    for i, sub_relation in enumerate(relation_string.split('.')):
        if i == 0:
            name_string = ont[sub_relation]['name']
            continue
        relation = ' "' + '_'.join(sub_relation.split('_')[:-1]) + '" '
        term = sub_relation.split('_')[-1]

        name_string += relation + ont[term]['name']
    return name_string


class Relations:
    def __init__(self, relations_of_interest, source_terms, target_term, ont, excluded_terms=None, print_=False):
        """
        Attributes:
            relations_of_interest: a list of relations that are relevant for finding relationship between the source
              and target term, e.g. ['is_a','is_model_for']
            source_terms: terms that we wish to look for relations from, list of the form [source_term_1, source_term_2,
                etc] such that we wish to find relationships of the form "source_term is_a target_term" or "source_term
                is_a other_term is_a target_term".
            target_term: term that we wish to look for relations to, e.g. source_term is_a target_term. Term string,
                either specific (e.g. 'FF:0000001') or general (e.g. 'FF')
            ont: Obo().ont object

        """
        # TODO: change _print, so that we just have logging.info of those levels.
        self.relations_of_interest = relations_of_interest
        self.source_terms = source_terms
        self.target_term = target_term
        if not excluded_terms:
            excluded_terms = []
        self.excluded_terms = excluded_terms
        self.relations = self.calculate(ont, print_)

    def calculate(self, ont, print_):
        # TODO: write how this works.
        relations = []
        for source_term in self.source_terms:
            relation_strings = [source_term]

            # we stop looking for a term, once we find a relation to the target_term or we we don't know where else to look:
            relation_found = False
            unchanged = False

            while (not relation_found) and (not unchanged):
                if print_:
                    time.sleep(0.2)
                    print(relation_strings)
                new_relation_strings = []
                for relation_string in relation_strings:
                    most_recent_term = relation_string.split('_')[-1]
                    for relation in self.relations_of_interest:
                        # Get new terms to check.
                        try:
                            new_terms = ont[most_recent_term][relation]
                        except:
                            new_terms = []

                        # For each new term, check for wanted relation.
                        for new_term in new_terms:
                            if new_term in self.excluded_terms:
                                continue

                            if new_term in relation_string:
                                logging.info(f'cyclic relationship: {relation_string}.{relation}_{new_term}')
                                continue
                            new_relation_string = relation_string + '.' + relation + '_' + new_term
                            new_relation_strings.append(new_relation_string)

                            # CHECK IF NEW TERM IS (ONE OF) TARGET TERM(S)
                            # if target_term is list of specific terms:
                            if isinstance(self.target_term, list) and (new_term in self.target_term):
                                relation_found = True
                            # if target_term is one specific term
                            elif (':' in self.target_term) and (self.target_term == new_term):
                                relation_found = True
                                break
                            # if term is general:
                            elif new_term.split(':')[0] == self.target_term:
                                relation_found = True
                                break
                        if relation_found:
                            break
                    if relation_found:
                        break

                if len(new_relation_strings) == 0:
                    unchanged = True
                relation_strings = new_relation_strings

            if relation_found:
                relations.append(new_relation_string)
            else:
                relations.append(np.nan)

        return pd.DataFrame(relations, index=self.source_terms)