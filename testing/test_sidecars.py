"""

ADD TEST for the following scenario: 

    The following tables demonstrate how mutual exclusive, required fields, may be set in rules.sidecars.*:

    MRIFuncRepetitionTime:
    selectors:
        - modality == "mri"
        - datatype == "func"
        - '!("VolumeTiming" in sidecar)'
        - match(extension, "^\.nii(\.gz)?$")
    fields:
        RepetitionTime:
        level: required
        level_addendum: mutually exclusive with `VolumeTiming`

    MRIFuncVolumeTiming:
    selectors:
        - modality == "mri"
        - datatype == "func"
        - '!("RepetitionTime" in sidecar)'
        - match(extension, "^\.nii(\.gz)?$")
    fields:
        VolumeTiming:
        level: required
        level_addendum: mutually exclusive with `RepetitionTime`


Expected behaviour:
    both are true at the beginning, i.e. valid metadata pieces. 
    if one is set, then it triggers a callback and disables the other. 

    to ensure this when checking within sidecar or metadata, it must only give the fields which have a 
    value set to it.
"""