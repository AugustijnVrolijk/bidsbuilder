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
            "sphinx.ext.napoleon", 
            "sphinx_autodoc_typehints",] 

autosummary_generate = True
autodoc_typehints = "description"

add_module_names = False
autodoc_class_signature = "separated"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": True,
} 
"""
members means it shows class methods, undoc-members means it shows class methods even if they have no docstring
and show-inheritance means it shows which class the class bases
add module names means it shortens the name to just be say TabularFile, rather than bidsbuilder.modules.file_bases etc...
"""

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = []
html_theme_options = {
    "navigation_with_keys": True,  # enable keyboard navigation (optional)
    "sidebar_hide_name": False,     # keep sidebar visible with project name
}

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))


