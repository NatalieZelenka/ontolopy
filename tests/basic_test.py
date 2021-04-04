import ontolopy as opy
import pytest
import os
import logging

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

@pytest.mark.download
def test_download_obo():
	# TODO: Test not allowed names
	# TODO: Delete before trying and check that works
	# TODO: Don't delete before trying and check logging input correct
	opy.download_obo('uberon-basic', out_dir=data_dir)

# TODO: sys.path stuff shouldn't be happening

@pytest.mark.download
def test_end_to_end():
	pass
	# TODO: write a new end-to-end test
	# TODO: tests marked download will only run with `pytest --download`. Think about when to run.
	# Tests downloading data:
	# out_file = obo.get_obo('sensory-minimal', out_dir='data/')
	# # Tests loading OBO into obo object:
	# obo_object = obo.Obo(out_file, ['UBERON'])
	# # Get relations between UBERON entities:
	# relations_of_interest = ['is_a', 'part_of']
	# source_terms = ['UBERON:0007622']  # "pecten oculi"
	# target_term = ['UBERON:0000047']  # "simple eye"
	# ont = obo_object.ont
	# _ = obo_object.Relations(relations_of_interest, source_terms, target_term, ont)


# TODO Add test for relations.relation_string_2_name_string


def test_obo_dict():
	basic_obo = os.path.join(data_dir, 'uberon.obo')
	ont = opy.Obo(file_loc=basic_obo, ont_ids=['UBERON'])
	assert(isinstance(ont.keys(), type({}.keys())))


def test_validate_term():
	assert(opy.validate_term(term_text='UBERON:13291823', allowed_ids=['UBERON']))
	assert(opy.validate_term(term_text='GO:1', allowed_ids=['GO', 'UBERON']))
	assert(not opy.validate_term(term_text='GO:13291823', allowed_ids=['UBERON']))
	assert(not opy.validate_term(term_text='UBERON', allowed_ids=['UBERON']))


def test_read_line_obo():
	ont_ids = ['NCBITaxon', 'UBERON']

	lines = {
		'id: UBERON:0000172': [('id', 'UBERON:0000172')],
		'synonym: "subpallium" NARROW [BTO:0003401, NCBITaxon:8782]':
			[('synonym', 'subpallium'), ('NCBITaxon', 'NCBITaxon:8782')]

	}
	for line, output in lines.items():
		line_list = line.split(' ')
		try:
			assert(opy.obo._read_line_obo(line_list, ont_ids) == output)
		except AssertionError:
			print(opy.obo._read_line_obo(line_list, ont_ids), output)
			raise
