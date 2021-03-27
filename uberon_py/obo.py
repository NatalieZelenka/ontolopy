import pandas as pd
import numpy as np
import time
import urllib.request as request
import os
import logging
# TODO: Add warnings/logging (remove all print statements)


def get_obo(data_name, out_dir='../data/'):
    # TODO: load from file:
    # TODO: Allow overwrite existing file

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


class Obo:
    def __init__(self, file_loc, ont_ids, root_terms=None):
        """
        Loads ontology from obo file into a dictionary of dictionaries.
        
        Attributes:
            file_loc: file location of obo (.obo file)
            ont: ontology dictionary of dictionaries of lists of related term IDs (1st level keys = term IDs, 2nd level keys = relationships)
        """
        self.file_loc = file_loc
        self.ont_ids = ont_ids
        self.ont = self.load_obo()
        self.root_terms = root_terms

    def load_obo(self):
        """
        Loads ontology from obo file into a dictionary of dictionaries.

        """
        terms = {}
        with open(self.file_loc) as f:
            term = {}
            for i, line in enumerate(f):
                line = line.strip()
                
                relation = None
                value = None
                line = line.strip().split(' ')
                if '[Term]' in line[0]:
                    if len(term)>0 and 'id' in term.keys():
                        if 'comment' in term.keys() and 'obsolete' in term['comment'].lower():
                            # print 'term ' + term['id'] + ': ' + term['name'] + ' is obsolete.'
                            term = {}
                            continue
                        elif term['id'].split(':')[0] in self.ont_ids:
                            terms[term['id']] = term
                    term = {}

                elif 'id:' in line[0] and 'alt_id:' not in line[0]:
                    ID = line[1]
                    term['id'] = ID

                elif line[0] == 'name:':
                    name = ' '.join(line[1:])
                    term['name'] = name

                elif 'comment:' in line[0]:
                    comment = ' '.join(line[1:])
                    term['comment'] = comment

                elif 'namespace:' in line[0]:
                    term['namespace'] = line[1]

                elif 'def:' in line[0]:
                    restOfLine = ' '.join(line[1:])
                    sources = restOfLine[restOfLine.find('[')+1:restOfLine.find(']')].split(',')

                    for source in sources:    
                        for ontIdentifier in self.ont_ids:
                                if ontIdentifier+':' in source:
                                    relation = ontIdentifier
                                    value = source

                elif 'consider:' in line[0]:
                    for ontID in self.ont_ids:
                        if ontID+':' in line[1]:
                            relation = ontID
                            value = line[1]

                elif line[0] == 'is_a:':
                    relation = 'is_a'
                    value = line[1]

                elif line[0] == 'relationship:':
                    # TODO: tidy this the hell up

                    if line[1] == 'derives_from':
                        relation = 'derives_from'
                        value = line[2]

                    elif line[1] == 'is_model_for':
                        relation = 'is_model_for'
                        value = line[2]

                    elif line[1] == 'develops_from':
                        relation = 'develops_from'
                        value = line[2]

                    elif line[1] == 'part_of':
                        relation = 'part_of'
                        value = line[2]

                    elif line[1] == 'never_in_taxon':
                        relation = 'never_in_taxon'
                        value = line[2]

                    elif line[1] == 'present_in_taxon':
                        relation = 'present_in_taxon'
                        value = line[2]

                    elif line[1] == 'only_in_taxon':
                        relation = 'only_in_taxon'
                        value = line[2]

                    elif line[1] == 'dubious_for_taxon':
                        relation = 'dubious_for_taxon'
                        value = line[2]

                    else:
                        # TODO: add logging here
                        relation = 'related_to'
                        value = line[2]

                elif line[0] == 'subset:':
                    relation = 'subset'
                    value=line[1]

                elif line[0] == 'intersection_of:':
                    if line[1] == 'part_of':
                        value = line[2]
                        relation = 'part_of'

                    elif line[1] == 'develops_from':
                        relation = 'develops_from'
                        value = line[2]

                    elif line[1] == 'derives_from':
                        relation = 'derives_from'
                        value = line[2]

                    else:
                        relation = 'intersection_of'
                        value = line[1]

                elif line[0] == 'union_of:':
                    relation = 'union_of'
                    value = line[1]

                elif line[0] == 'synonym:':
                    synonym = (' '.join(line)).split('"')[1]

                    try:
                        term['synonyms'].append(synonym.lower())
                    except:     
                        term['synonyms'] = [synonym.lower()]
                    restOfLine = ' '.join(line[1:])
                    for ontID in self.ont_ids:
                        if ontID in restOfLine:
                            ontTerms =restOfLine[restOfLine.find("[")+1:restOfLine.find("]")]
                            ontTerms = ontTerms.split(',')
                            for ontTerm in ontTerms:
                                ontTerm = ontTerm.replace(' ','')
                                if ontID+':' not in ontTerm:
                                    continue    
                                relation = ontID
                                value = ontTerm

                elif line[0] == 'xref:':
                    for ontID in self.ont_ids:
                        if ontID in line[1]:
                            relation = ontID
                            value = line[1]

                if relation is not None and value is not None:

                    try:
                        term[relation].append(value)
                    except:
                        term[relation] = [value]

                    for ontID in self.ont_ids:
                        if ontID in value:
                            try:
                                term[ontID].append(value)
                            except:
                                term[ontID] = [value]
        return terms
    
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
        return self.Relations(relations_of_interest,source_terms,target_term,ont)
    

def relation_string_2_name_string(ont, relation_string):
    for i, subrelation in enumerate(relation_string.split('.')):
        if i == 0:
            name_string = ont[subrelation]['name']
            continue
        relation = ' "' + '_'.join(subrelation.split('_')[:-1]) + '" '
        term = subrelation.split('_')[-1]

        name_string += relation + ont[term]['name']
    return name_string


class Relations:
    def __init__(self, relations_of_interest, source_terms, target_term, ont, excluded_terms=None, print_=False):
        """
        Attributes:
            relations_of_interest: a list of relations that are relevant for finding relationship between the source and target term, e.g. ['is_a','is_model_for']
            source_terms: terms that we wish to look for relations from, list of the form [source_term_1, source_term_2, etc] such that we wish to find relationships of the form "source_term is_a target_term" or "source_term is_a other_term is_a target_term".            
            target_term: term that we wish to look for relations to, e.g. source_term is_a target_term. Term string, either specific (e.g. 'FF:0000001') or general (e.g. 'FF')
            relations: pandas dataframe with source_terms as index and relation_strings (or NaN) in relation_string column.
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
            relation_strings =[source_term]

            #we stop looking for a term, once we find a relation to the target_term or we we don't know where else to look:
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
                        #Get new terms to check.
                        try:
                            new_terms = ont[most_recent_term][relation]
                        except:
                            new_terms = []

                        #For each new term, check for wanted relation.
                        for new_term in new_terms:
                            if new_term in self.excluded_terms:
                                continue

                            if new_term in relation_string:
                                logging.info(f'cyclic relationship: {relation_string}.{relation}_{new_term}')
                                continue
                            new_relation_string = relation_string + '.' + relation + '_' + new_term
                            new_relation_strings.append(new_relation_string)
                            
                            # CHECK IF NEW TERM IS (ONE OF) TARGET TERM(S)
                            #if target_term is list of specific terms:
                            if isinstance(self.target_term,list) and (new_term in self.target_term):
                                relation_found = True
                            #if target_term is one specific term
                            elif (':' in self.target_term) and (self.target_term == new_term):
                                relation_found = True
                                break
                            #if term is general:
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

