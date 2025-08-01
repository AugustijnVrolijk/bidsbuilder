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
            "sphinx.ext.autosummary",
            "sphinx_autodoc_typehints",] 

autosummary_generate = True
autodoc_typehints = "description"

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ['_static']
html_theme_options = {
    "navigation_with_keys": True,  # enable keyboard navigation (optional)
    "sidebar_hide_name": False,     # keep sidebar visible with project name
}

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))


