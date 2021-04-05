"""
This module contains code for creating and working with the Uberon class: ontology containing Uberon terms.
"""
import logging
import pandas as pd

from .obo import Obo
from .relations import Relations

# TODO: Properly consider this architecture. Seems a bit weird :/.


def uberon_from_obo(obo):
    """
    Creates an `Uberon` object from an `Obo` object.
    Uberon objects have additional functions they can use.

    :param obo: `Obo` object
    :return uberon: `Uberon` object
    """
    uberon = Uberon()
    for term, value in obo.items():
        uberon[term] = value

    for att_key, att_val in obo.__dict__.items():
        uberon.__dict__[att_key] = att_val

    uberon._check_terms()

    return uberon


class Uberon(Obo):
    """
    An UBERON-specific ontology object.
    """

    def __init__(self):
        self._check_terms()

    def _check_terms(self):
        if len(self.terms) == 0:
            return None

        try:
            assert('UBERON' in {x.split(':')[0] for x in self.terms})
        except AssertionError:
            logging.error(f"There are no UBERON terms in your Uberon object.")

    def sample_map_by_ont(self, sample_ids: list, exclude=None, relation_types=None, to=None):
        """
        Map tissues from sample names to uberon identifiers. Will only work if ontology contains Uberon + Sample terms.

        :param sample_ids: list of sample identifiers
        :param exclude: list of tissues to exclude, i.e. because they are too general.
        :param relation_types: list of relation types in ontology that relate to position in body.
        :param to: list of ontology prefixes that you want to map to.
        :return:
        """

        if exclude is None:
            exclude = [
                'UBERON:0000061',  # anatomical structure
                'UBERON:0000479',  # tissue
                'UBERON:0000467',  # anatomical system
                'UBERON:0011216',  # organ system subdivision
                'UBERON:0000922',  # embryo
                'CL:0000048',  # multi fate stem cell
            ]
        else:
            assert(isinstance(exclude, list))

        if relation_types is None:
            relation_types = [
                'is_a',
                'related_to',
                'part_of',
                'derives_from',
                'intersection_of',
                'union_of',
                'is_model_for',
                'replaced_by',
                'develops_from',
            ]
        else:
            assert(isinstance(relation_types, list))

        if to is None:
            to = ['UBERON']
        else:
            assert(isinstance(to, list))

        tissue_relations = Relations(
            allowed_relations=relation_types,
            sources=sample_ids,
            targets=to,
            ont=self,
            excluded=exclude,
        )

        return tissue_relations

    def sample_map_by_name(self, sample_names):
        """
        Map tissues from sample identifiers to uberon identifers.

        :param sample_names: must have sample identifiers for index, and tissue/sample descriptors/names for values.
        :return:
        """

        # TODO: Make samples_names allowed as a dict or a pandas

        name2uberon = []
        for sample_id, tissue_name in sample_names.iterrows():
            found = False
            tissue_name = tissue_name.lower()
            for uberon_term in self.keys():
                try:
                    synonyms = self[uberon_term]['synonyms']
                except KeyError:
                    synonyms = []
                if (self[uberon_term]['name'].lower() == tissue_name) or (tissue_name in synonyms):
                    name2uberon.append([sample_id, uberon_term, tissue_name])
                    found = True
            if not found:
                name2uberon.append([sample_id, None, tissue_name])

        name2uberon = pd.DataFrame(name2uberon, columns=['Sample ID', 'UBERON', 'name matched on'])
        name2uberon = name2uberon.set_index('Sample ID')
        return name2uberon

    # TODO: Write restrict_to_taxon, would need to read in NCBI ontology, since it is hierarchical (e.g. vertebrates)
    # def restrict_to_taxon(ont, ncbi_id, valid_terms = ['UBERON'], keep_dubious=False, only_yes=False):
    #     """
    #     Loops through valid_terms terms in ontology `ont`, and removes any that are never in taxon with ID `ncbi_id`
    #     """
    #     yes_relations = ['only_in_taxon', 'present_in_taxon']
    #     never = 'never_in_taxon'
    #     dubious = 'dubious_for_taxon'

    #     for term in ont.keys():
    #         if term.split(':')[0] not in valid_terms:
    #             continue

