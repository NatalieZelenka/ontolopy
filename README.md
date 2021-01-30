# `uberon_py`: a python package for the Uberon ontology
:construction: :construction: This package is under development :construction: :construction: 

## Summary
I created this package to be able to easily interrogate relationships between Uberon terms in Python. 

## Installation
`uberon_py` is available on pip, and can be installed using:
```bash
pip3 install uberon_py
```

## Usage
Example usage:

```python
import uberon_py

# read an ontology in obo format
obo = uberon_py.Obo('path_to_file/uberon_ext.obo')

# find relationships between terms of interest:
# (in this case, are any of the source_terms, is_a or part_of the brain?)
source_terms = ['UBERON:0003290','UBERON:0003369','UBERON:0003703'] 
target_terms = ['UBERON:0000955'] #  brain term
relations_of_interest  = 'is_a','part_of']
relations = uberon_py.Relations(source_terms,target_terms,relations_of_interest[,obo.ont).relations
```
