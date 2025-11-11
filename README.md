# bidsbuilder provides a schema-driven pythonic object representation of all BIDS components. #

bidsbuilder provides a schema-driven, Pythonic object representation of all BIDS components, interpreting the BIDS schema (https://github.com/bids-standard/bids-specification/tree/master/src/schema) using the bidsschematools library and a BIDS-language interpreter.

By interpreting the schema, bidsbuilder precisely defines naming convention, file metadata, file types and more. It features base classes representing every possible type of BIDS components, from metadata json files to the entities that compose a filename. To enhance this object representation, bidsbuilder adds a dependency-tracking hook system that attaches schema-driven validation to the relevant files and attributes, providing real-time feedback and ensuring that metadata and file naming conventions are dynamically validated as users build their dataset.

This dynamic feedback loop boosts robustness, fault tolerance, and flexibility by offering immediate feedback when errors are detected, without interrupting the workflow. Unlike traditional static checkers, which stop the process when a single mistake occurs, this system allows users to continue building their dataset with any correct data already inputted. Even if certain metadata or filenames are incorrect, the user can still work with the valid parts of the dataset and address errors incrementally, rather than having to restart the entire process from scratch.

Currently features:
* Tree representation of folder for retrieval of objects via their paths
* Interpreter for schema selectors and checks
* Dependancy-tracking hooks
* Base classes for BIDS components

Future features:
* Configuration for auto-completing metadata
* Tools for bulk completion of metadata parameters
* Conversion of raw data to bids-approved formats

Possible future features:
* Web-based UI to easily modify and interact with datasets without needing to use Python

## ROADMAP ##

Next features in order:
* ~~final schema interpreter features~~
    * ~~create tests comparing to meta.expression_tests to align interpreter~~
    * ~~add tag system to speedup callback calling speed~~
* ~~Dynamic descriptor classes for callback and field support~~
    * ~~base descriptor classes~~
    * ~~adding custom getters, input validators~~
    * ~~support for container types, dynamic upgrading to observable types~~
    * ~~dynamic descriptor classes to combine features (single/multi callback),(container/normal), etc..~~
    * metaclass support to decorate observability on any container
* full schema object support
    * ~~Finish metadata class - recursive metadata containerisation (when metadata stores more metadata)~~
    * ~~Finish val setters for all types (suffix, datatype, entity, etc..)~~
    * ~~Finish columns class~~
    * Add tests to verify values objects and name-value objetcs, as well as proper val setting checking
    * Add support to lookup info for value terms (modalities, etc..)
* fix dataset data folders
    * Fix subject/session/datatype class
    * ~~Integrate subject with dataset files (participants.tsv, etc..)~~
    * Add support for folder level files (scans.tsv, sessions.tsv)
* tabular file support
    * ~~Create tabular file class~~
    * Integrate seperate TSV-sidecar-JSON class with tabular
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
