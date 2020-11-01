import sys
sys.path.append('../')
sys.path.append('.')
import uberon_py.obo as obo


def test_basic():
	# Tests downloading data:
	out_file = obo.get_obo('sensory-minimal', out_dir='data/')
	# Tests loading OBO into obo object:
	obo_object = obo.Obo(out_file, ['UBERON'])
	# Get relations between UBERON entities:
	relations_of_interest = ['is_a', 'part_of']
	source_terms = ['UBERON:0007622']  # pecten oculi
	target_term = ['UBERON:0000047']  # simple eye
	ont = obo_object.ont
	_ = obo_object.Relations(relations_of_interest, source_terms, target_term, ont)

