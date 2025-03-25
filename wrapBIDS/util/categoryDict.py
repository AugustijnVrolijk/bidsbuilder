import re
import json
from pathlib import Path

class catDict():
    def __init__(self, categories:list=["required","recommended","optional"]):
        self.categories = categories
        self.defaultCat = categories[-1]
        self.combined = {}
        
        for cat in categories:
            setattr(self, cat, {})

    def __setitem__(self, key, value):
        tKey, category = self._resolve_key(key)
        getattr(self, category)[tKey] = value        
        self.combined[tKey] = value

    def __getitem__(self, key):
        tKey, _ = self._resolve_key(key)
        return self.combined[tKey]
    
    def _resolve_key(self, key):
        #resolve possible key input into format: key, category
        if isinstance(key, str):
            #split chars are currently: ',;'
            parts = [part.strip() for part in re.split(r'[,;]+', key.strip())]

            if len(parts) <= 2:
                key = tuple(parts)
            else:
                raise ValueError(f", or ; cannot be used as part of the key name, only to seperate the key from the category")

        if isinstance(key, list):
            key = tuple(key)

        if isinstance(key, tuple):
            tempKey = []
            for subKey in key:
                if not isinstance(subKey, str):
                    raise TypeError(f"Key and category must be a string inside the tuple")
                tempKey.append(subKey.strip())
            key = tuple(tempKey)

            if len(key) == 2:
                k, k2 = key
                if k2 in self.categories:
                    return (k, k2)
                elif k in self.categories:
                    return (k2, k)
                else:
                    raise ValueError(f"Category must be one of: {self.categories}")
            elif len(key) == 1:
                return (key[0], self.defaultCat)
            
            else:
                raise ValueError(f"too many or no keys found in {key}")
            
        raise ValueError(f"key was given in incorrect format, use string tuple or list")
    
    def pop(self, key):
        tKey, category = self._resolve_key(key)
        getattr(self, category).pop(tKey)
        return self.combined.pop(tKey)
    
    def items(self):
        return self.combined.items()
    
    def __repr__(self):
        return f"catDict({self.combined})"

    def _write_JSON(self, path):
       pass

    def _read_JSON(self, path, **kwargs):
        #**kwargs is a dictionary defining categories for names
        if path[-5:] != ".json":
            raise ValueError(f"file {path} is not a json")
        
        with open(path, 'r') as f:
            jsonString = f.read()
            vals = json.loads(jsonString)
            if not isinstance(vals, dict):
                raise ValueError(f"File {path} is a json containing {vals}, not a dict which was expected")

            for cat, keys in kwargs.items():
                for key in keys:
                    val = vals.pop(key, None)  
                    self.__setattr__((key, cat),val)
                
            for key,value in vals.items():
                
                pass
                

        """
        read JSON File and populate catDict object.
        """
        pass

def main():
    testDict = catDict()
    testDict["tester"] = 1243
    print("hello")
    pass


if __name__ == "__main__":
    main()


"""
https://github.com/mne-tools/mne-bids/blob/main/mne_bids/utils.py#L228
https://github.com/mne-tools/mne-bids/blob/main/mne_bids/write.py

def _write_json(fname, dictionary, overwrite=False):
    #Write JSON to a file.
    fname = Path(fname)
    if fname.exists() and not overwrite:
        raise FileExistsError(
            f'"{fname}" already exists. Please set overwrite to True.'
        )

    json_output = json.dumps(dictionary, indent=4, ensure_ascii=False)
    with open(fname, "w", encoding="utf-8") as fid:
        fid.write(json_output)
        fid.write("\n")

    logger.info(f"Writing '{fname}'...")

"""