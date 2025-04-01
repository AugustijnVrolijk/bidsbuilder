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