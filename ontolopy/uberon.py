"""
This module contains code for creating and working with the Uberon class: ontology containing Uberon terms.
"""
import logging
import pandas as pd
import numpy as np

from .obo import Obo, _extract_synonym, _extract_synonym_type
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

    def sample_map_by_ont(self, sample_ids: list, exclude=None, relation_types=None, to=None, child_mapping=False):
        """
        Map tissues from sample names to uberon identifiers. Will only work if ontology contains Uberon + Sample terms.

        :param sample_ids: list of sample identifiers
        :param exclude: list of tissues to exclude, i.e. because they are too general.
        :param relation_types: list of relation types in ontology that relate to position in body.
        :param to: list of ontology prefixes that you want to map to.
        :param child_mapping: If True, searches children instead of parents.
        :return:
        """

        # TODO: add child_mapping functionality
        if exclude is None:
            exclude = [
                'UBERON:0000061',  # anatomical structure
                'UBERON:0000479',  # tissue
                'UBERON:0000467',  # anatomical system
                'UBERON:0011216',  # organ system subdivision
                'UBERON:0000922',  # embryo
                'UBERON:0007023',  # adult organism
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
                # 'is_model_for',
                'replaced_by',
                # 'develops_from',
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

    def sample_map_by_name(self, sample_names, to=None, col_names=None, xref=None, synonym_types=None):
        """
        Map tissues from sample identifiers to uberon identifers.

        :param sample_names: map from sample identifiers to tissue/sample descriptors/names for values.
          May be `dict` or `pd.Series`
        :param to: list of ontology prefixes that you want to map to.
        :param xref: An ontology identifier (e.g. FMA) the presence of which denotes a preferred term.
        :param col_names: Column names of returned relationships
        :return:
        """

        # TODO: Currently mapping each name once for each sample... Should just get a a unique name list and go through that.

        # TODO: Make more general (like Relations) and move to Obo() as might want to look at other types of matched
        #  names such as phenotype.

        # TODO: Add terms to exclude
        if col_names is None:
            col_names = ['from', 'name_matched_on', 'to']
        else:
            assert(len(col_names) == 3)

        if to is None:
            to = ['UBERON']
        else:
            assert(isinstance(to, list))

        if isinstance(sample_names, dict):
            sample_names = pd.Series(sample_names)
        assert(isinstance(sample_names, pd.Series))

        if synonym_types is None:
            synonym_types = ['EXACT', 'BROAD', 'NARROW']
        else:
            assert(isinstance(synonym_types, list))

        name_to_uberon = {}
        for tissue_name in sample_names.unique():
            found = False
            options = []
            if pd.isna(tissue_name):
                name_to_uberon[tissue_name] = np.nan
                continue

            tissue_name_l = tissue_name.lower()
            for uberon_term in self.terms:

                if uberon_term.split(':')[0] not in to:
                    continue

                if self[uberon_term]['name'].lower() == tissue_name_l:
                    name_to_uberon[tissue_name] = uberon_term
                    found = True
                    break

                try:
                    synonyms_info = self[uberon_term]['synonym']
                except KeyError:
                    continue

                # TODO: Allow change allowed syn types
                for synonym_info in synonyms_info:
                    syn_type = _extract_synonym_type(synonym_info)
                    if syn_type not in synonym_types:
                        continue
                    synonym = _extract_synonym(synonym_info)

                    if tissue_name_l == synonym:
                        # TODO: Check Taxon requirements here
                        options.append((tissue_name, uberon_term, syn_type))
                        found = True

            if not found:
                name_to_uberon[tissue_name] = np.nan
            elif len(options) == 1:
                tissue_name, uberon_term, _ = options[0]
                name_to_uberon[tissue_name] = uberon_term
            elif len(options) >= 1:  # Choose best option of synonyms:
                chosen = False

                # Check for XREF to preferred ontology (e.g. FMA for human)
                if xref is not None:
                    for option in options:
                        tissue_name, uberon_term, _ = option
                        if xref in self[uberon_term].keys():
                            chosen = option

                if not chosen:
                    # TODO: If no XREF choose most specific/most exact synonym? (Currently just pick first)
                    chosen = options[0]
                tissue_name, uberon_term, _ = chosen
                name_to_uberon[tissue_name] = uberon_term

        # Create sample_to_uberon
        sample_to_uberon = pd.DataFrame(columns=col_names[1:], index=sample_names.keys())
        sample_to_uberon.index.rename(col_names[0], inplace=True)
        sample_to_uberon[col_names[1]] = sample_names
        sample_to_uberon[col_names[2]] = sample_names.map(name_to_uberon)

        return sample_to_uberon

    def get_overall_tissue_mappings(self, map_by_name, map_by_ont, rel=None):
        """
        Combines the two mappings `map_by_name` and `map_by_ont` to create an overall mapping and disagreements.

        :param map_by_name: mapping from sample to tissue via sample name, from `Uberon.sample_map_by_name`.
        :type map_by_name: class: `pd.DataFrame`
        :param map_by_ont: mapping from sample to tissue via sample ontology ID, from `Uberon.sample_map_by_ont`.
        :type map_by_ont: class: `pd.DataFrame`
        :parm rel: list of relation strings allowed between name and ontology mappings to count as not a disagreement.
        :type rel: `list`.
        :return: (`overall_mapping`: mapping from sample to tissue combining both sources,
          `disagreements`: disagreements between "by name" and "by ontology" mappings.)
        :rtype: (class: `pd.DataFrame`, class: `pd.DataFrame`)
        """

        samples = list(map_by_ont.index)
        assert(isinstance(map_by_name, pd.DataFrame))
        assert(isinstance(map_by_ont, pd.DataFrame))
        assert(set(map_by_ont.index) == set(map_by_name.index))

        if rel is None:
            rel = Obo._relationships
        assert(isinstance(rel, list))

        map_by_name = map_by_name[~map_by_name.index.duplicated(keep='first')]
        map_by_ont = map_by_ont[~map_by_ont.index.duplicated(keep='first')]

        assert(len(map_by_ont.index) == len(map_by_name.index))

        # Preparing outputs
        mapping_columns = ['sample_id', 'by_name', 'by_ont', 'overall', 'mapped_by']
        overall_mapping = pd.DataFrame(index=map_by_name.index, columns=mapping_columns[1:])
        overall_mapping.index.rename(mapping_columns[0], inplace=True)

        disagreement_columns = ['sample_id', 'by_name', 'by_ont', 'relation_between', 'name_label']
        disagreements = pd.DataFrame(columns=disagreement_columns[1:])
        disagreements.index.rename(disagreement_columns[0], inplace=True)

        for sample in samples:
            # check if mappable by name:
            name_matched_on, by_name = map_by_name.loc[sample]

            # check if mappable by ontology:
            relation_text, by_ont = map_by_ont.loc[sample][1:]

            if not pd.isna(by_name) and pd.isna(by_ont):  # by name only
                overall = by_name
                mapped_using = "name"
            elif not pd.isna(by_ont) and pd.isna(by_name):  # by ont only
                overall = by_ont
                mapped_using = "ontology"
            elif pd.isna(by_name) and pd.isna(by_ont):  # both unmappable
                overall = np.nan
                mapped_using = np.nan
            elif by_name == by_ont:  # both the same
                overall = by_ont
                mapped_using = "both (same)"
            elif by_name != by_ont:  # mappable but different
                name_to_ont = Relations(allowed_relations=rel,
                                        sources=[by_name],
                                        targets=[by_ont],
                                        ont=self).loc[by_name, 'to']
                ont_to_name = Relations(allowed_relations=rel,
                                        sources=[by_ont],
                                        targets=[by_name],
                                        ont=self).loc[by_ont, 'to']

                if pd.isna(name_to_ont) and pd.isna(ont_to_name):  # no relation between by_ont and by_name
                    disagreements.loc[sample] = [by_name, by_ont, relation_text, name_matched_on]
                    overall = by_name
                    mapped_using = "name"
                elif pd.isna(name_to_ont) and not pd.isna(ont_to_name):  # If one is (part of) another:
                    overall = by_name
                    mapped_using = "name"
                    logging.info("name", ont_to_name)
                elif not pd.isna(name_to_ont) and pd.isna(ont_to_name):
                    overall = by_ont
                    mapped_using = "ontology"
                    logging.info("ont", name_to_ont)
            overall_mapping.loc[sample] = [by_name, by_ont, overall, mapped_using]

        return overall_mapping, disagreements

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

