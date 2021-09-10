# Changelog

[//]: # (TODO: Link to GitHub releases)

## [1.1.1-beta](https://github.com//NatalieThurlby/ontolopy/compare/1.1.1-beta...1.1.0-beta)
Bug fix:
 - `opy.obo._extract_synonym` used by `opy.Uberon.map_by_name` wasn't stripping whitespace, so missed some mapped names.

## [1.1.0-beta](https://github.com//NatalieThurlby/ontolopy/compare/1.0.2-beta...1.1.0-beta)
- New functionality:
    - `Obo()` class:
        - Added `opy.Obo.merge()`: merge one ontology into another.
        - Added `opy.Obo.from_dict()`: create `Obo()` from a dictionary.
        - Added `opy.Obo.copy()`: copies `Obo()` object.
        - Separated `load_obo` from `Obo()` class.
        - Added local functions that are used to extract synonyms and synonym types from synonym strings.
    - new `opy.uberon` module, containing:
        - `Uberon()` class that inherits from `Obo()`, including `sample_map_by_ont` method.
        - `uberon_from_obo` function
    - new `Relations.format_all` method.
- Refactoring:
    - Made the static class variables for reading ontologies private variables.
    - Refactored `opy.relations.Relations` class to subclass Pandas DataFrame.
- Testing:    
    - Added test for `obo.Obo.merge()`.
    - Updated tests to include new behaviour for synonyms
- Documentation:
    - Improved docstrings for `Obo()` class.
    - Set up sphinx autodoc and used to document `Obo()` class.

## [1.0.2-beta](https://github.com//NatalieThurlby/ontolopy/compare/1.0.1-beta...1.0.2-beta)
- Fixed GitHub action for versioned docs [[#9](https://github.com/NatalieThurlby/ontolopy/issues/9)]

## [1.0.1-beta](https://github.com/NatalieThurlby/ontolopy/releases/tag/1.0.1-beta)
- Got documentation on gh-pages [[#2](https://github.com/NatalieThurlby/ontolopy/issues/2)]
- Wrote sphinx extension to be able to access versioned docs (not yet easy to navigate)
- Removed TravisCI for testing, and added GitHub Actions for testing, deploying docs, and packaging [[#1](https://github.com/NatalieThurlby/ontolopy/issues/1)].

## Ontolopy 1.0.0-beta
- Renamed module to Ontolopy [[#4](https://github.com/NatalieThurlby/ontolopy/issues/4)]
- Refactored `Obo()` and `Relations()` class.
- `Obo()` now extends `dict`.
- Added unit tests for `ontolopy.validate_term()` and `ontolopy.read_line_obo()`.
- Added basic contents for Sphinx documentation [[#2](https://github.com/NatalieThurlby/ontolopy/issues/2)], with PyData Sphinx theme.

## uberon-py 0.1.0
- Download `.obo` files: ["sensory-minimal"](http://ontologies.berkeleybop.org/uberon/subsets/sensory-minimal.obo), ["uberon-extended"](http://purl.obolibrary.org/obo/uberon/ext.obo) and ["uberon-basic"](http://purl.obolibrary.org/obo/uberon.obo)
- Load `.obo` files: added `Obo()` class.
- Find relations in ontology terms: added `Relations()` class.
- Continuous Integration using TravisCI
- Released `uberon-py` on pypi
