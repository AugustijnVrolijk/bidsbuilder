import re
import json
from pathlib import Path

class catDict(dict):
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

    def populateSelf(self, rawDict, **kwargs):
        for cat, keys in kwargs.items():
            for key in keys:
                val = vals.pop(key, None)  
                self.__setattr__((key, cat),val)
            
        for key,value in vals.items():
            
            pass
        
def popDicts(toPop:catDict, rawDict:dict, **kwargs):

    pass
        

def main():
    testDict = catDict()
    testDict["tester"] = 1243

    print("hello")
    pass


if __name__ == "__main__":
    main()




