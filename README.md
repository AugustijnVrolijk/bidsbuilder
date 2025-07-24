# bidsbuilder is a library facilitating the creation of BIDS approved datasets via schema-driven pythonic objects of all required files and metadata. #

bidsbuilder interprets the bids schema (https://github.com/bids-standard/bids-specification/tree/master/src/schema) using the bidsschematools library and a bids-language interpreter.

The interpreted schema enables quick retrieval of required metadata when adding data, bidsbuilder complements this by adding a system of hooks based on schema selectors and checks, enabling dynamic changing of required metadata linked to schema dependencies.

Base classes are added to support core functions such as json sidecars, tabular data files, paths from entities and more.

All features can be reached via the use of a BidsDataset object, which integrates all other modules to allow for an easily modifiable and customisable dataset wrapper.

Currently features:
* Tree representation of folder for retrieval of objects via their paths
* Interpreter for schema selectors and checks
* Base classes for common files

Future features:
* Base classes for data files
* Configuration for auto-completing metadata
* Advanced tools for bulk completion of metadata parameters
* Conversion of raw data to bids-approved formats

Possible future features:
* Web-based UI to easily modify and interact with datasets without needing to use Python

## ROADMAP ##

Next features in order:
* callbacks on selectors
    * Finish metadata class
* tabular file support
    * Finish columns class
    * Create tabular file class
    * Integrate seperate TSV-sidecar-JSON class with tabular
* fix dataset data folders
    * Fix subject/session/datatype class
    * Integrate subject with dataset files (participants.tsv, etc..)
    * Add support for folder level files (scans.tsv, sessions.tsv)
* support for data adding
    * Update data_collections class
    * Add support for all possible sidecar files (tabular and json, i.e. coordsystem.json)
* raw data conversion
    * link to mne library, conversion of raw data (file path) via mne to bids approved format
* clean docs
    * add tutorial/guide
    * hide API for non-user facing functions/classes
    * clean up general page layout/look
* add thorough testing
    * stuff like meta.associations
    * general unit tests etc..