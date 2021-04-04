# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys
from distutils.util import convert_path

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

# get version:
ns = {}
ver_path = convert_path('../ontolopy/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), ns)

# The full version, including alpha/beta/rc tags
release = f"v{ns['__version__']}"

sys.path.append(os.path.abspath("./_ext"))
extensions = ['versioned-tagged-docs']

# -- Project information -----------------------------------------------------

project = 'ontolopy'
copyright = '2021, Natalie Thurlby'
author = 'Natalie Thurlby'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx._ext.*') or your custom
# ones.
extensions += [
    'myst_nb',
    "sphinxarg.ext",
    'sphinx.ext.autosummary',
]
autosummary_generate = True


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    'github_url': 'https://github.com/NatalieThurlby/ontolopy',
    'twitter_url': 'https://twitter.com/hashtag/ontolopy',
    'search_bar_text': 'Search this site...',
    'search_bar_position': 'navbar',
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/ontolopy",
            "icon": "fas fa-box-open",
        }
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_favicon = '_static/favicon.png'
