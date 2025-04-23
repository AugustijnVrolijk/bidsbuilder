tools and scripts to convert data from the ASPEN database at UMC utrecht into a BIDS friendly format


Input: -Github BIDS schema, YAML format so machine readable, can be used to define classes, requirments and options etc...

        Kinds of data:
            - Raw data (in unknown format) -> use MNE-BIDS tools to convert
            - Data complementing raw data (JSON sidecars) 
            - Unknown data -> must be manually filled in (authors, readme, etc...)

UI:

    Let you choose paths, for raw data /sidecar jsons.
    have mapping dictionaries to allow for automatic conversion of data under different "key" names to the required ones
    (i.e. in editable config).
    Options to select and write down unknown data that must be manually filled in.


FILES HAVE:
    core files (and their fields)

    deriv files
        (comprise of entities - name)
        (accompanied by json sidecar - fields)

    raw files:
        (comprise of entities - name)
        (accompanied by json sidecar - fields)


SCHEMA: using bidsschematools
    - objects : descriptions for pretty much everything you need (files, what they do, entities, etc..)
    - rules : the nitty gritty stuff, whether stuff is required, what entities it needs etc...
            - files: describes the requirements for files, as well as entities, datatypes extensions etc...


Create a dataset Tree. 
Can build it from rules/directories.yaml to describe core files / folders.
Inate tree structure to allow for backwards and forwards parsing for inheritance of METADATA

When a "dataset" is created, all the required directories / files are created, from rules/files/common/core etc.. 
with options for their metadata.  
Options are added to add raw data. Then this is parsed through its specific file type modality/entity etc... updating relevant core files.

