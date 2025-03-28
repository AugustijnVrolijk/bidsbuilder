import json
from pathlib import Path

def _write_JSON(path, data, overwrite = False):
    fname = Path(fname)
    if fname.exists() and not overwrite:
        raise FileExistsError(
            f'"{fname}" already exists. Please set overwrite to True.'
        )

    json_output = json.dumps(data, indent=4, ensure_ascii=False)
    with open(fname, "w", encoding="utf-8") as f:
        f.write(json_output)
        f.write("\n")
    

def _read_JSON(path):
    #**kwargs is a dictionary defining categories for names
    if path[-5:] != ".json":
        raise ValueError(f"file {path} is not a json")
    
    with open(path, 'r') as f:
        jsonString = f.read()
        vals = json.loads(jsonString)
        if not isinstance(vals, dict):
            raise ValueError(f"File {path} is a json containing {vals}, not a dict which was expected")

        return vals
    
"""
https://github.com/mne-tools/mne-bids/blob/main/mne_bids/utils.py#L228
https://github.com/mne-tools/mne-bids/blob/main/mne_bids/write.py
"""