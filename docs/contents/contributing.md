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

---
These materials were adapted from the [Bristol RSE team](https://www.bristol.ac.uk/acrc/research-software-engineering/)'s [Metawards Development Guide](https://metawards.org/versions/1.5.1/development.html).