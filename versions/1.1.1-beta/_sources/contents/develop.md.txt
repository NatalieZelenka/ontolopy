# Development

[//]: # (TODO: Write about all-contributors, how to contribute ideas, PRs, etc)

## Developers
Ontolopy was developed by Natalie Thurlby. 
Please [contact me](mailto:NatalieThurlby@bristol.ac.uk) for any communications related to Ontolopy.

## Philosophy
Ontolopy was developed for [Natalie's thesis](https://nataliethurlby.github.io/phenotype_from_genotype).
While to some degree, Ontolopy benefits from Research Software Engineering best practices such as automated testing, semantic versioning, versioned docs, and continuous integration, there is also much more that could be done to increase reliability and usability (particularly in terms of test and tutorial coverage).

Please see the [roadmap](./roadmap) to read about future directions for Ontolopy.

## Developer guidance

### Style 
Ontolopy uses the following conventions and programming style:
- Python-style naming conventions:
    - Packages: lowercase (single word)
    - Classes: CamelCase
    - Methods, Functions, Variables: snake_case
- Functions with leading underscores (e.g. `_extract_source()`)  are meant for internal use only.
- Relative imports should be used at all times, with imports ideally delayed until they are needed.

### Development workflow
1. Create a [new GitHub issue](https://github.com/NatalieThurlby/ontolopy/issues/new) or comment on an existing issue, saying what you are planning on working on and when.
2. Develop on a feature branch, which should branch off the `main` branch:
    - To test locally, run `pytest` at root.
    - Build the book locally, run `sphinx-build docs docs/_build/html`.
    - To build dist files locally, run `python3 setup.py sdist`, and to install those local dist files, you can run `pip3 install -e .`.
3. Create a [new PR](https://github.com/NatalieThurlby/ontolopy/compare) (Pull Request) from the feature branch to the `dev` branch (this will trigger tests through the `run-tests.yml` GitHub Action)

### Creating a new release
This is the current process for creating a new PyPI and GitHub release:
- Once the PR from dev into main is passing all checks
- Someone will approve the PR from `dev` into `main`
- Run `python3 setup.py sdist bdist_wheel` on `main` to create dist files to upload when doing GitHub release.
- fill in the changelog in the docs
- Create a [new release](https://github.com/NatalieThurlby/ontolopy/releases/new), filling in the checklist
  - copy the changelog to the GitHub release
  - tag the release with the **exact same version number** as the number in `ontolopy/version.py` (the action will fail otherwise)
  - upload the distribution files. 
- Creating the release will automatically run a GitHub action that distributes the package on pypi and stores a version of the docs that will remain available. Check that it was successful.

### Ontolopy's GitHub Actions
Ontolopy uses GitHub Actions for Continuous Integration to automate updating the docs, running tests, and distributing the package.
The actions are: 
- [`deploy-site.yml`](https://github.com/NatalieThurlby/ontolopy/actions/workflows/deploy-site.yml): deploys docs (latest) when changes are pulled into `dev`.
- [`new-release.yml`](https://github.com/NatalieThurlby/ontolopy/actions/workflows/new-release.yml): deploys/updates the versioned docs, and distributes package to pypi with twine when a new release is made from `main`.
- [`run-tests.yml`](https://github.com/NatalieThurlby/ontolopy/actions/workflows/run-tests.yml): runs  tests using [pytest](https://docs.pytest.org/en/stable/) when changes are pushed/pulled into `main` or `dev`.

---
These materials were adapted from the [Bristol RSE team](https://www.bristol.ac.uk/acrc/research-software-engineering/)'s [Metawards Development Guide](https://metawards.org/versions/1.5.1/development.html).