from __future__ import annotations

class dictview():
    """
    enables <inefficient> storing of dictionaries
    Used to allow for storing/modifying of multiple observableDicts, and not clash with their
    callback methods. (i.e. specific callbacks different to each unique dicts)

    Notes:
        when fetching entities for a file, or say json metadata of a json. It creates a "super" dict/list by combining
        the values unique to the instance, plus those of its parent (shared by many instances)
        But these higher up instances may have different callbacks, i.e. if I have a file:
        sub-test/ses-one/eeg/sub-test_ses-one_eeg.json
        and the user fetches this instances metadata (which inherits dataset_description.json)
        and then wants to change idk, authors. Then it needs to update to the correct dictionary. I.e. dataset_description.json
        and along with it call the correct callbacks.

        
        need to think of how intuitive this may be

        in an alternate case, for the same file referenced above, if a user changes it's datatype, I assume they'd expect
        the specific file to move to the new datatype folder, rather than change the datatype of all files which its currently under.

        Need to do a system where if someone modifies a property out of the instances scope,
        rather than changing the property to all related files, it instead resolves it and moves the instance
        in order to cleanly do this.
        im thinking of the way compositeFilename is done, and ideally I don't want to necessarily fully seperate
        subjects, sessions, datatypes into seperate filename classes.
    """