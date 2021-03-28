# Changelog

[//]: # (TODO: Link to GitHub releases)

## 1.0.0-beta
- Renamed module to Ontolopy. 
- Refactored `Obo()` and `Relations()` class.
- `Obo()` now extends `dict`.
- Added unit tests for `ontolopy.validate_term()` and `ontolopy.read_line_obo()`.
- Added Sphinx documentation, with PyData Sphinx theme.

## 0.1.0
- Download `.obo` files: ["sensory-minimal"](http://ontologies.berkeleybop.org/uberon/subsets/sensory-minimal.obo), ["uberon-extended"](http://purl.obolibrary.org/obo/uberon/ext.obo) and ["uberon-basic"](http://purl.obolibrary.org/obo/uberon.obo)
- Load `.obo` files: added `Obo()` class.
- Find relations in ontology terms: added `Relations()` class.
- Continuous Integration using TravisCI
- Released `uberon-py` on pypi
