import json
from pathlib import Path
from mne.utils import logger

def _write_JSON(path, data, overwrite = False):
    print(path)
    fname = Path(path)
    if fname.exists() and not overwrite:
        raise FileExistsError(
            f'"{fname}" already exists. Please set overwrite to True.'
        )

    json_output = json.dumps(data, indent=4, ensure_ascii=False)
    with open(fname, "w", encoding="utf-8") as f:
        f.write(json_output)
        f.write("\n")

    logger.info(f"writing JSON at '{path}'")

def _read_JSON(path):
    #**kwargs is a dictionary defining categories for names
    fname = Path(path)
    if not fname.exists():
        raise LookupError(f"file {fname} does not exist")

    if fname.suffix != ".json":
        raise ValueError(f"file {fname} is not a json")
    
    with open(fname, 'r') as f:
        jsonString = f.read()
        vals = json.loads(jsonString)
        if not isinstance(vals, dict):
            raise ValueError(f"File {path} is a json containing {vals}, not a dict which was expected")

        return vals
    
"""
https://github.com/mne-tools/mne-bids/blob/main/mne_bids/utils.py#L228
https://github.com/mne-tools/mne-bids/blob/main/mne_bids/write.py
"""