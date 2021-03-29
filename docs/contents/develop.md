# Development

[//]: # (TODO: Write about all-contributors, how to contribute ideas, PRs, etc)

## Developers
Ontolopy was developed by Natalie Thurlby. Please [contact me](mailto:NatalieThurlby@bristol.ac.uk) for any communications related to Ontolopy.

## Philosophy
Ontolopy was developed for [Natalie's thesis](https://nataliethurlby.github.io/phenotype_from_genotype).
While Ontolopy benefits from Research Software Engineering best practices such as automated testing, created versioned docs, and continuous integration, to some degree, there is also much more that could be done to increase test coverage and usability.

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
2. Develop on a feature branch, which should branch off the `main` branch.
3. Create a [new PR](https://github.com/NatalieThurlby/ontolopy/compare) (Pull Request) from the feature branch to the `dev` branch (this will trigger tests through the `run-tests.yml` GitHub Action)
- test locally before pushing (run `pytest` at root) to GitHub

### Install local development version
local development:
`python3 setup.py sdist`
`pip3 install -e .`

## Build local docs
`cd docs`

`sphinx-build . _build/html`

## Release
This is the current process for releasing:
- Once the PR from dev into main is passing all checks
- Someone will approve the PR from `dev` into `main`
- Run `python3 setup.py sdist bdist_wheel` on `main` to create dist files to upload when doing GitHub release.
- fill in the changelog in the docs
- edit the drafted release, filling in the checklist
  - copy the changelog to the GitHub release
  - tag the release with the **exact same version number** as the number in `ontolopy/version.py` (the action will fail otherwise)
- this will automatically run a GitHub action that distributes the package on pypi and stores a version of the docs that will remain available.

## Ontolopy GitHub Actions
Ontolopy uses GitHub Actions for Continuous Integration to automate updating the docs, running tests, and distributing the package.
The actions are: 
- [`deploy-site.yml`](https://github.com/NatalieThurlby/ontolopy/actions/workflows/deploy-site.yml): deploys docs (latest) when changes are pulled into `dev`.
- [`new-release.yml`](https://github.com/NatalieThurlby/ontolopy/actions/workflows/new-release.yml): deploys/updates the versioned docs, and distributes package to pypi with twine when a new release is made from `main`.
- [`run-tests.yml`](https://github.com/NatalieThurlby/ontolopy/actions/workflows/run-tests.yml): runs  tests using [pytest](https://docs.pytest.org/en/stable/) when changes are pushed/pulled into `main` or `dev`.

---
These materials were adapted from the [Bristol RSE team](https://www.bristol.ac.uk/acrc/research-software-engineering/)'s [Metawards Development Guide](https://metawards.org/versions/1.5.1/development.html).