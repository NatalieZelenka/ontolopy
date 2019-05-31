import pytest
import sys
import os
sys.path.append('../')
sys.path.append('.')
import uberon_py.obo as obo


def data_test():
	# Download small uberon data set:
	try:
		out_file = obo.get_obo('sensory-minimal',out_dir = 'data/')
		return out_file
	except:
		 pytest.fail("Could not get data")
		 return None


def load_test(obo_file):
	try:
		obo_object = obo.Obo(obo_file,['UBERON'])
		return obo_object
	except:
		pytest.fail("Could not load obo file")
		return None


def relations_test(obo_object):
	# Get relations between UBERON entities:
	try:
		relations_of_interest = ['is_a','part_of']
		source_terms = ['UBERON:0007622']  # pecten oculi
		target_term = ['UBERON:0000047']  # simple eye
		ont = obo_object.ont
		relations = obo_object.Relations(relations_of_interest,source_terms,target_term,ont)
		return relations
	except:
		pytest.fail("Could not get relations between entities")
	return None


data = data_test()
obo_obj = load_test(data)
relations = relations_test(obo_obj)
