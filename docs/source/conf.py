# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'bidsbuilder'
copyright = '2025, Augustijn Vrolijk'
author = 'Augustijn Vrolijk'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc",
            "sphinx.ext.napoleon",  # If using Google/NumPy-style docstrings
            "sphinx.ext.autosummary",
            "sphinx_autodoc_typehints",
            "myst_parser",]  # If you're using Markdown]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",          # for Google/NumPy docstring styles
    "sphinx_autodoc_typehints",     # show type hints
]

autodoc_typehints = "description"

html_theme = "furo"
