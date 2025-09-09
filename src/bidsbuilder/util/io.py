import json
import pandas as pd

import os

from pathlib import Path
from mne.utils import logger

def _write_tsv(path:str, data:pd.DataFrame, overwrite:bool = False):
    fname = Path(path)
    if fname.exists() and not overwrite:
        raise FileExistsError(
            f'"{fname}" already exists. Please set overwrite to True.'
        )
    
    args = {"sep":"\t","index":False, "na_rep":"n/a"}
    if fname.suffix == ".gz" or fname.suffixes[-1] == ".gz":
        args["compression"] = "gzip"
    else:

        # check: https://bids-specification.readthedocs.io/en/stable/common-principles.html#tabular-files
        # at the time of writing 20/08/2025 motion files which end in .tsv MUST not have a header...
        # Ideally want to add some meta schema to make this all more automated...
        stem = fname.stem
        for _ in fname.suffixes:
            stem = Path(stem).stem

        last_keyword = stem.split("_")[-1]
        if last_keyword == "motion":
            args["header"] = False
        else:
            args["header"] = True

    data.to_csv(fname,**args)


def _write_json(path, data, overwrite = False):
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