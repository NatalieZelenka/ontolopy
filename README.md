# `uberon-py`: a python package for the Uberon ontology
:construction: :construction: This package is under development (particularly the documentation) :construction: :construction: 

## Summary
I created this package to be able to easily interrogate relationships between Uberon terms in Python. 

## Usage
Example usage:
```
# read an ontology in obo format
obo = uberon-py.Obo('path_to_file/uberon_ext.obo')

# find relationships between terms of interest:
# (in this case, are any of the source_terms, is_a or part_of the brain?)
source_terms = ['UBERON:0003290','UBERON:0003369','UBERON:0003703'] 
target_terms = ['UBERON:0000955'] #  brain term
relations_of_interest  = 'is_a','part_of']
relations = uberon-py.Relations(source_terms,target_terms,relations_of_interest[,obo.ont).relations

```
