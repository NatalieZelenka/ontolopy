"""
This module contains code for creating and working with the Obo class: objects that represent ontologies.
"""

import pandas as pd
import urllib.request as request
import os
import logging
import validators


def download_obo(data_name, out_dir='../data/'):
    """
    Download obo from a list of known locations.

    :param data_name: Name of OBO you wish to download.
    :param out_dir: Directory in which to save OBO file.
    :return out_file: path to saved file.
    """
    # TODO: Allow overwrite existing file
    # TODO: test

    uberon_urls = {
    'sensory-minimal':'http://ontologies.berkeleybop.org/uberon/subsets/sensory-minimal.obo',
    'uberon-extended': 'http://purl.obolibrary.org/obo/uberon/ext.obo',
    'uberon-basic': 'http://purl.obolibrary.org/obo/uberon.obo',
    }

    if data_name not in uberon_urls.keys():
        supported_list = '\n'.join(uberon_urls.keys())
        logging.error(f'`data_name` {data_name} not in supported list:\n{supported_list}')

    url = uberon_urls[data_name]
    file_name = (os.path.basename(url))
    out_file = os.path.join(out_dir, file_name)

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        logging.info(f'Created directory {out_dir}.')

    if os.path.isfile(out_file):
        logging.warning(f'File already exists at location: {os.path.abspath(out_file)}. Cancelling download.')
        return out_file

    # TODO: make sure behaviour is sensible if url doesn't exist. (Write test).
    file_data = request.urlopen(url) 
    data_to_write = file_data.read() 
    logging.info(f'Downloaded {data_name} from: {url}')

    with open(out_file, 'wb') as f:
        f.write(data_to_write)

    logging.info(f'Wrote {data_name} file to: {os.path.abspath(out_file)}')
    return out_file


def _validate_term(term_text: str, allowed_ids: list):
    """
    Check term is a valid format.

    :param term_text: text to validate, e.g. "NCBITaxon:9606" or "UBERON:12391203".
    :param allowed_ids: a list of allowed identifier prefixes, e.g. ['GO', 'UBERON'] or None if dont' want to restrict.
    :return: bool True=valid, False=not
    """
    assert(isinstance(term_text, str))
    if not allowed_ids:
        assert(isinstance(allowed_ids, list))
    if ':' not in term_text:
        return False
    elif (allowed_ids and (term_text.split(':')[0] in allowed_ids)):
        return True


def _find_all(haystack, needle):
    idx = -1
    while True:
        idx = haystack.find(needle, idx + 1)
        if idx == -1:
            break
        yield idx


def _find(s: str, ch: str) -> list:
    """
    Finds indices of character `ch` in string `s`
    """
    return [i for i, ltr in enumerate(s) if ltr == ch]


def _between_chars(s: str, ch1: str, ch2=None) -> str:
    if ch2 is None:
        # i1, i2 = _find(s, ch1)[:2]
        i1, i2 = [x for x in _find_all(s, ch1)][:2]
    else:
        i1 = s.find(ch1)
        i2 = s.find(ch2)
    return s[i1 + 1: i2]


def _extract_synonym(rest_of_line: str) -> str:
    """
    Extracts synonym name from obo line.
    :param rest_of_line: string containing line except for "synonym: "
    :return:
    """
    synonym = rest_of_line.split('"')[1].lower()
    return synonym


def _extract_synonym_type(rest_of_line:str) -> str:
    _, i1 = [x for x in _find_all(rest_of_line, '"')][:2]
    i2 = rest_of_line.find('[')
    return rest_of_line[i1+1: i2].strip()


def _read_line_obo(line_list: list, ont_ids: list):
    """
    Reads a line of an obo file, and returns a list of (relation, value) tuples. Most lines will only contain one.
    :param line_list: list of line elements (original line split by spaces)
    :param ont_ids: allowed ontology ids (list): None if want to keep all IDs.
    :return new_relations: a list of (relation, value) tuples
    """

    if not ont_ids:
        assert(isinstance(ont_ids, list))
    assert(isinstance(line_list, list))

    line_list[0] = line_list[0].replace(':', '')
    new_relations = []  # list of (relation, value) tuples.

    if line_list[0] in Obo._text_attributes:
        new_relations.append((line_list[0], ' '.join(line_list[1:])))

    elif line_list[0] in Obo._attributes:
        new_relations.append((line_list[0], line_list[1]))

    elif line_list[0] in Obo._relationships:
        new_relations.append((line_list[0], line_list[1]))

    elif line_list[0] in Obo._nestable_attributes:
        if line_list[1] in Obo._relationships:
            new_relations.append((line_list[1], line_list[2]))
        elif ':' in line_list[1]:
            new_relations.append((line_list[0], line_list[1]))
        elif ':' in line_list[2]:
            # TODO: Add test
            logging.info(f'Relationship {line_list[1]} is not currently stored.'
                         f' saving as {line_list[0]}. {line_list[2]}.')
            new_relations.append((line_list[0], line_list[2]))
        else:
            logging.warning(f'Line looks unusual: {" ".join(line_list)}')

    elif line_list[0] == 'synonym':
        rest = ' '.join(line_list[1:])  # rest of line

        source_relations = _extract_source(rest, ont_ids)
        new_relations += source_relations

        new_relations.append((line_list[0], rest))

    elif line_list[0] == 'def':
        # TODO: update to contain
        rest = ' '.join(line_list[1:])
        new_relations.append((line_list[0], rest))
        new_relations += _extract_source(rest, ont_ids)

    elif line_list[0] == 'xref':
        if _validate_term(line_list[1], ont_ids):
            new_relations.append((line_list[0], line_list[1]))

    # TODO: add logging info for unrecognised lines

    return new_relations


def _extract_source(text, ont_ids):
    """
    In obo files sources are written between square brackets. Currently does not keep URL sources (e.g. wikipedia).

    :param text:
    :param ont_ids: list of allowed ontology ids , e.g. ['GO', 'HP'], or None if don't want to restrict.
    :return new_relations: list of (relation, value) tuples, e.g. [('xref': 'HP:091231')]
    # TODO: What kind of relations should sources be? 'xref'? My own, e.g. 'source'/'source.synonym'/'source.GO.synonym'
    """
    new_relations = []
    sources = [x.strip() for x in _between_chars(text, '[', ']').split(',')]
    for source in sources:
        if _validate_term(source, ont_ids):
            # TODO: explain in Ontolopy part
            new_relations.append((source.split(':')[0], source))
        elif validators.url(source):
            new_relations.append(('url', source))
    return new_relations


def _merge_dict(a, b, prefer='self', path=None):
    """
    Recursively merges dictionary a into dictionary b. Prefers a.

    :param a: dictionary a (self)
    :param b: dictionary b (new)
    :param path: used in recursion
    :return:
    """
    c = a.copy()
    if path is None:
        path = []
    for key in b:
        if key in c:
            if isinstance(c[key], dict) and isinstance(b[key], dict):
                _merge_dict(c[key], b[key], path + [str(key)])
            elif c[key] == b[key]:
                pass  # same leaf value
            elif isinstance(c[key], list) and isinstance(b[key], list):
                c[key] = list(set(b[key]) | set(c[key]))
            else:
                if key == 'namespace':
                    c[key] = f"Combined {c[key]} and {b[key]}"
                elif key == 'name':
                    # we expect some differences in name, due to e.g. terms becoming obsolete
                    logging.info(f"Unmatching names: {c[key]} =/= {b[key]}, keeping the former.")
                else:
                    logging.error(f"For key {key}, {c[key]} =/= {b[key]}. Choosing {prefer}.")
                    if prefer == 'new':
                        c[key] = b[key]
        else:
            c[key] = b[key]
    assert (len(c) == (len(a) + len(b) - len(set(a.keys()) & set(b.keys()))))
    return c


def load_obo(file_loc, ont_ids=None, discard_obsolete=True):
    """
    Loads ontology from `.obo` file at `file_loc`.

    :param file_loc: file location - path to stored obo file.
    :param ont_ids: list of ontology ids, e.g. `['UBERON', 'CL']`
    :param discard_obsolete: if True discard obsolete terms.
    :return: `Obo` ontology object.
    """
    obo = Obo()
    # TODO: check for version/date of ontology file and save if possible
    # terms = {}
    if not ont_ids:
        assert(isinstance(ont_ids, list))
    with open(file_loc) as f:
        term = {}
        for i, line in enumerate(f):
            line = line.strip()
            line = line.strip().split(' ')

            if '[Term]' in line[0]:
                if len(term) > 0 and 'id' in term.keys():
                    if 'comment' in term.keys() and 'obsolete' in term['comment'].lower() and discard_obsolete:
                        logging.info(f"term {term['id']}: {term['name']} is obsolete. Discarding.")
                        term = {}
                        continue
                    elif (not ont_ids) or (ont_ids and (term['id'].split(':')[0] in ont_ids)):
                        obo[term['id']] = term
                term = {}

            new_relations = _read_line_obo(line, ont_ids)
            for (relation, value) in new_relations:
                if relation in Obo._strings:
                    term[relation] = value
                    continue
                try:
                    term[relation].append(value)
                except KeyError:
                    term[relation] = [value]

    return obo


class Obo(dict):
    """
    Creates `Obo` ontology object from `dict` with ontology terms for keys, mapping to term attributes and relations.

    Each key/term is a dictionary with key: value pairs mapping either:

    1. Attribute (`str`) to value (`str`), e.g. `'name': 'scapula'`

    2. Type of relationship (`str`) to term identifiers (`list`), e.g. `'is_a': ['UBERON:0002513']`

    Info: Obo stands for Open Biological Ontology: a popular file format for building biological ontologies.
    """

    # TODO: tidy so that all attributes are organised in a dict with type (string, list), acceptable formats, nestable
    _strings = [  # must be strings not lists
        'name',
        'id'
    ]

    _nestable_attributes = [
        'relationship',
        'intersection_of',
    ]

    _text_attributes = [
        'name',
        'comments',
    ]

    _attributes = [
        'id',
        'alt_id',
        'subset',
        'is_obsolete',  # TODO: add test
        'replaced_by',  # TODO: add test
        'namespace',
        'consider',
    ]

    _relationships = [
        'is_a',
        'union_of',
        'derives_from',
        'is_model_for',
        'develops_from',
        'part_of',
        'never_in_taxon',
        'present_in_taxon',
        'only_in_taxon',
        'dubious_for_taxon',
        # TODO: test from here down:
        'capable_of',
        'has_part',
        'channel_for',
        'capable_of_part_of',
        'positively_regulates',
        'negatively_regulates',
        'regulates',
        'connects',
        'attaches_to',
        'adjacent_to',
        'drains',
        'supplies',
        'composed_primarily_of',
        'skeleton_of',
        'developmentally_replaces',
        'located_in',
        'produced_by',
        'extends_fibers_into',
        'has_potential_to_develop_into',
        'continuous_with',
    ]

    def __init__(self, source_dict=dict()):
        """
        Initialise self from a source dictionary.

        :param source_dict: `dict` mapping terms to their attributes and relationships.
        """
        # Note: when adding attributes consider how this will effect self.merge()
        assert(isinstance(source_dict, dict))
        self._from_dict(source_dict)

    def __copy__(self):
        copy = Obo(dict(self).copy())

        for att_key, att_val in self.__dict__.items():
            copy.__dict__[att_key] = att_val

        return copy

    # TODO: Write __deepcopy__

    @property
    def terms(self):
        """
        The ontology terms (a `dict_keys` object).
        :return:
        """
        return self.keys()

    @property
    def leaves(self):
        """
        Leaf terms are the most specific terms in the ontology; they have no children, only parents (a `set` object).
        :return:
        """
        return self._get_leaves()

    # TODO: Write roots(), get_roots()

    def _from_dict(self, source_dict):
        """
        Create Obo() from a Python dict.
        :param source_dict: dictionary object from which to create `Obo`
        :return:
        """
        assert(isinstance(source_dict, dict))
        for term, value in source_dict.items():
            self[term] = value
        return self

    def terms_from(self, ont_id: list):
        """
        Returns a set of terms in Obo ontology with prefix in list ont_id
        :param ont_id: list of ontology prefixes e.g. ['HP', 'GO']
        :return:
        """
        return {x for x in self.terms if x.split(':')[0] in ont_id}
    
    # def get_relations(self, relations_of_interest, source_terms, target_term, ont):
    #     """
    #     get_relations finds all relationships (based on relations_of_interest e.g. ['is_a']) between terms like source
    #     _term and terms like target_term, e.g. source_term is_a target_term. Returns a mapping between term and most
    #     specific (least number of steps) relationstring (if one exists, else NaN) for each relevant term in the
    #     ontology.
    #
    #     Args:
    #         relations_of_interest: a list of relations that are relevant for finding relationship between the source
    #         and target term, e.g. ['is_a','is_model_for']
    #         source_terms: terms that we wish to look for relations from, list of the form [source_term_1,
    #         source_term_2, etc] such that we wish to find relationships of the form "source_term is_a target_term" or
    #         "source_term is_a other_term is_a target_term".
    #         target_term: term that we wish to look for relations to, e.g. source_term is_a target_term. Term string,
    #         either specific (e.g. 'FF:0000001') or general (e.g. 'FF')
    #
    #     Returns:
    #         Relations class object, containing relations (see relations class for details), relations_of_interest,
    #         source_term and target_term
    #
    #     """
    #     return relations.Relations(relations_of_interest, source_terms, target_term, ont)

    def merge(self, new, prefer='self'):
        """
        Recursively merges `new` into `self` and returns a merged `Obo` ontology.

        :param new: Obo object (or list of objects) to add.
        :param prefer: prefer 'self' (base Obo) or 'new' (new Obo)
        :return merged: A merged Obo
        """

        if isinstance(new, list):
            # create merged ontology
            merged = new[0].copy()
            for obo in new[1:]:
                merged = self.merge(obo)
            return merged

        # TODO: Make merge work for an arbitrary number of ontologies (must be ordered by preference)
        prefer_options = ['self', 'new']
        try:
            assert(prefer in prefer_options)
        except AssertionError:
            logging.error(f"`prefer` must be in {str(prefer_options)}, not {prefer}.")

        merged = _merge_dict(self, new, prefer)
        return Obo(merged)

    def _get_leaves(self, term_types=None, relations_of_interest=None):
        """
        Get the leaf terms from the ontology only.

        :param term_types: if given, a list of term types to restrict to (e.g. ['UBERON', 'GO']
        :param relations_of_interest: if given, a list of relation types to restrict to (e.g. 'is_a', 'part_of')
        :return:
        """
        if not relations_of_interest:
            relations_of_interest = self._relationships + self._nestable_attributes
        else:
            assert(isinstance(relations_of_interest, list))

        leaves = set(self.terms)
        if term_types is not None:
            assert (isinstance(term_types, list))
            assert (
                all([':' not in x for x in term_types]))  # don't want 'UBERON:1231239' must be of form 'UBERON', 'GO'
            leaves = {x for x in leaves if x.split(':')[0] in term_types}

        for term in self.terms:
            for relation in self[term].keys():
                if relation not in relations_of_interest:
                    continue
                related_terms = self[term][relation]
                assert(isinstance(related_terms, list))
                leaves -= set(related_terms)

        return leaves

    # TODO: Write to_json()
