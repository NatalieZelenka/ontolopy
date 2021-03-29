# Contributing

[//]: # (TODO: Write about all-contributors)

## Development

### Style guide
- We follow the following Python-style naming conventions.
    - Packages: lowercase (single word)
    - Classes: CamelCase
    - Methods, Functions, Variables: snake_case
- Functions with leading underscores (e.g. `_extract_source()`)  are meant for internal use only.
- Relative imports should be used at all times, with imports ideally delayed until they are needed.

## How-tos

### Start developing
- comment on an existing GitHub issue, or make a new GitHub issue and comment on it, saying what you are planning on working on and when.
- develop on a feature branch, which should branch from the 'dev' branch
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

## Our GitHub Actions
[//]: # (TODO: fill in other GH actions)
We use GitHub Actions to automate updating the docs, running tests, and distributing the package:
- `deploy-site.yml`: deploys docs (latest) when changes are pushed/pulled into `main`.

---
These materials were adapted from the [Bristol RSE team](https://www.bristol.ac.uk/acrc/research-software-engineering/)'s [Metawards Development Guide](https://metawards.org/versions/1.5.1/development.html).