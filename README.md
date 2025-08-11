# bidsbuilder provieds a schema-driven pythonic object representation of all BIDS components. #

bidsbuilder interprets the bids schema (https://github.com/bids-standard/bids-specification/tree/master/src/schema) using the bidsschematools library and a bids-language interpreter.

The interpreted schema precisely declares naming convention, file metadata, file types and more. bidsbuilder has base classes representing every possible type of BIDS components, from metadata json files to the entities that make up a filename. This object representation is complemented by adding a dependency-tracking hook system that attaches schema-driven validation to relevant files and attributes, providing real-time feedback and ensuring that metadata and file naming conventions are dynamically validated throughout the dataset creation process.

This dynamic feedback loop enhances robustness, fault tolerance, and flexibility by providing users with direct, real-time feedback whenever mistakes are made, without disrupting their entire workflow. Unlike traditional static checkers, which halt progress when a single error is found, this system allows users to build their dataset with whatever correct data is available, ensuring that no progress is lost. Even if certain metadata or names are incorrect, users can still see and work with the valid portions of their dataset, making it possible to address issues incrementally rather than restarting from scratch.

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
* Dynamic descriptor classes for callback and field support
    * ~~base descriptor classes~~
    * ~~adding custom getters, input validators~~
    * ~~support for container types, dynamic upgrading to observable types~~
    * ~~dynamic descriptor classes to combine features (single/multi callback),(container/normal), etc..~~
    * metaclass support to decorate observability on any container
* full schema object support
    * ~~Finish metadata class - recursive metadata containerisation (when metadata stores more metadata)~~
    * ~~Finish val setters for all types (suffix, datatype, entity, etc..)~~
    * Finish columns class
    * Add support to lookup info for value terms (modalities, etc..)
* fix dataset data folders
    * Fix subject/session/datatype class
    * Integrate subject with dataset files (participants.tsv, etc..)
    * Add support for folder level files (scans.tsv, sessions.tsv)
* tabular file support
    * Create tabular file class
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
