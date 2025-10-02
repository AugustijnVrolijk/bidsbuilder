# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SRC_DIR = ../src/bidsbuilder
API_DIR = source
DOCS_DIR = .

# Remove old API docs and regenerate
apidoc:
	rm -rf $(API_DIR)/*
	sphinx-apidoc -o $(API_DIR) $(SRC_DIR) -f -e --separate

# Build HTML documentation
html: apidoc
	sphinx-build -b html $(DOCS_DIR) _build/html

.PHONY: apidoc html