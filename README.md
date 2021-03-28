# Ontolo**py** a python package for working with .obo files
:construction: This package is in development :construction:

## Installation
Ontolopy is available on pip, and can be installed using:

```bash
pip install ontolopy
```

## Usage
Example usage:

```python
import ontolopy

# read an ontology in obo format
obo = ontolopy.Obo('path_to_file/uberon_ext.obo')

# find relationships between terms of interest:
# (in this case, are any of the source_terms, is_a or part_of the brain?)
source_terms = ['UBERON:0003290','UBERON:0003369','UBERON:0003703'] 
target_terms = ['UBERON:0000955'] #  brain term
relations_of_interest  = ['is_a','part_of']
relations = ontolopy.Relations(source_terms,target_terms,relations_of_interest,obo.ont).relations
```
