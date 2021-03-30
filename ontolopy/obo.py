import pandas as pd
import urllib.request as request
import os
import logging
import pprint


# TODO: separate into relations and obo files at minimum

def get_obo(data_name, out_dir='../data/'):
    # TODO: load from file:
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


def validate_term(term_text, allowed_ids):
    """
    :param term_text: text to validate, e.g. "NCBITaxon:9606" or "UBERON:12391203".
    :param allowed_ids: a list of allowed identifier prefixes, e.g. ['GO', 'UBERON']
    :return: bool True=valid, False=not
    """
    assert(isinstance(term_text, str))
    assert(isinstance(allowed_ids, list))
    if ':' not in term_text:
        return False
    elif term_text.split(':')[0] in allowed_ids:
        return True


def _read_line_obo(line_list, ont_ids):
    """
    Reads a line of an obo file, and returns a list of (relation, value) tuples. Most lines will only contain one.
    :param line_list: list of line elements (original line split by spaces)
    :param ont_ids: allowed ontology ids (list)
    :return new_relations: a list of (relation, value) tuples
    """

    assert(isinstance(ont_ids, list))
    assert(isinstance(line_list, list))

    line_list[0] = line_list[0].replace(':', '')
    new_relations = []  # list of (relation, value) tuples.

    if line_list[0] in Obo._text_attributes:
        new_relations.append((line_list[0], ' '.join(line_list[1:])))

    elif line_list[0] in Obo._attributes:
        new_relations.append((line_list[0], line_list[1]))

    elif line_list[0] in Obo._nestable_attributes:
        if line_list[1] in Obo._relationships:
            new_relations.append((line_list[1], line_list[2]))
        elif ':' in line_list[1]:
            new_relations.append((line_list[0], line_list[1]))
        else:
            # TODO: Add test
            logging.error(f'Unknown relationship {line_list[1]} for value {line_list[2]}, saving as {line_list[0]}.')

    elif line_list[0] == 'synonym':
        synonym = (' '.join(line_list)).split('"')[1].lower()
        new_relations.append((line_list[0], synonym))

        rest = ' '.join(line_list[1:])  # rest of line
        new_relations += _extract_source(rest, ont_ids)

    elif line_list[0] == 'def':
        rest = ' '.join(line_list[1:])
        new_relations.append((line_list[0], rest))
        new_relations += _extract_source(rest, ont_ids)

    elif line_list[0] == 'xref':
        if validate_term(line_list[1], ont_ids):
            new_relations.append((line_list[0], line_list[1]))

    # TODO: add logging info for unrecognised lines

    return new_relations


def _extract_source(text, ont_ids):
    """
    In obo files sources are written between square brackets. Currently does not keep URL sources (e.g. wikipedia).
    :param text:
    :param ont_ids: list of allowed ontology ids , e.g. ['GO', 'HP']
    :return new_relations: list of (relation, value) tuples, e.g. [('xref': 'HP:091231')]
    # TODO: also keep urls
    # TODO: What kind of relations should sources be? 'xref'? My own, e.g. 'source'/'source.synonym'
    """
    new_relations = []
    source_terms = [x.strip() for x in text[text.find("[") + 1:text.find("]")].split(',')]
    for source_term in source_terms:
        if validate_term(source_term, ont_ids):
            new_relations.append((source_term.split(':')[0], source_term))
    return new_relations


def _merge_dict(a, b, prefer='self', path=None):
    """
    Recursively merges dictionary a into dictionary b. Prefers a.
    :param a:
    :param b:
    :param path:
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


def load_obo(file_loc, ont_ids, discard_obsolete=True):
    """
    Loads ontology from obo file into a dictionary of dictionaries.

    """
    obo = Obo()
    # TODO: check for version/date of ontology file and save if possible
    # terms = {}
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
                    elif term['id'].split(':')[0] in ont_ids:
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
    # TODO: tidy so that all attributes are organised in a dict with type (string, list), acceptable formats, nestable

    _strings = [  # must be strings not lists
        'name',
        'id'
    ]

    _nestable_attributes = [
        'relationships',
        'intersection_of',
    ]

    _text_attributes = [
        'name',
        'comments',
    ]

    _attributes = [
        'id',
        'alt_id',
        'is_a',
        'subset',
        'is_obsolete',  # TODO: add test
        'replaced_by',  # TODO: add test
        'union_of',
        'namespace',
        'consider',
    ]
    _relationships = [
        'derives_from',
        'is_model_for',
        'develops_from',
        'part_of',
        'never_in_taxon',
        'present_in_taxon',
        'only_in_taxon',
        'dubious_for_taxon',
    ]

    def __init__(self, dict_=dict()):
        """
        """
        # TODO: other attributes (note must also be changed in merge).
        self.from_dict(dict_)

    def from_dict(self, dict_):
        """
        Create Obo() from a Python dict.
        :param dict_:
        :return:
        """
        assert(isinstance(type(dict_), dict))
        for term, value in dict_.items():
            self[term] = value
        return self

    def copy(self):
        copy = dict(self).copy()

        for att_key, att_val in self.items():



    def map_tissue_name_to_uberon(self, design_df, tissue_name_column):
        # TODO: Make an UBERON class that is a child of Ontolgy
        """Assumes that the sample name is the index of the design_df"""
        samples_names = design_df[[tissue_name_column]].dropna()
        
        name2uberon = []
        for sample_id, row in samples_names.iterrows():
            tissue_name = row[tissue_name_column]
            found = False
            tissue_name = tissue_name.lower()
            for uberon_term in self.ont.keys():
                try:
                    synonyms = self.ont[uberon_term]['synonyms']
                except:
                    synonyms = []
                if (self.ont[uberon_term]['name'].lower() == tissue_name) or (tissue_name in synonyms):
                    name2uberon.append([sample_id, uberon_term, tissue_name])
                    found = True
            if not found:
                name2uberon.append([sample_id, None, tissue_name])
        
        name2uberon = pd.DataFrame(name2uberon, columns=['Sample ID', 'UBERON', 'name matched on'])
        name2uberon = name2uberon.set_index('Sample ID')
        return name2uberon
    
    def get_relations(self, relations_of_interest, source_terms, target_term, ont):
        """
        get_relations finds all relationships (based on relations_of_interest e.g. ['is_a']) between terms like source_term and terms like target_term, e.g. source_term is_a target_term. Returns a mapping between term and most specific (least number of steps) relationstring (if one exists, else NaN) for each relevant term in the ontology.
        
        Args:
            relations_of_interest: a list of relations that are relevant for finding relationship between the source and target term, e.g. ['is_a','is_model_for']
            source_terms: terms that we wish to look for relations from, list of the form [source_term_1, source_term_2, etc] such that we wish to find relationships of the form "source_term is_a target_term" or "source_term is_a other_term is_a target_term".
            target_term: term that we wish to look for relations to, e.g. source_term is_a target_term. Term string, either specific (e.g. 'FF:0000001') or general (e.g. 'FF')

        Returns:
            Relations class object, containing relations (see relations class for details), relations_of_interest, source_term and target_term
            
        """
        return self.Relations(relations_of_interest, source_terms, target_term, ont)

    def merge(self, new, prefer='self'):
        """
        Recursively merges `new` into Obo.
        :param new: Obo object to add.
        :param prefer: prefer 'self' (base Obo) or 'new' (new Obo)
        :return merged: A merged Obo
        """
        prefer_options = ['self', 'new']
        try:
            assert(prefer in prefer_options)
        except AssertionError:
            logging.error(f"`prefer` must be in {str(prefer_options)}, not {prefer}.")

        merged = _merge_dict(self, new, prefer)
        return merged

