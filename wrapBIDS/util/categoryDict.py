import re
from mne.utils import logger

class catDict(dict):
    def __init__(self, categories:list=["required","recommended","optional"], defaultCatidx: None|int = -1):
        super().__init__()
        self.categories = categories
    
        if defaultCatidx is None:
            self.defaultCat = None
        else:
            self.defaultCat = categories[defaultCatidx]

        for cat in categories:
            setattr(self, cat, {})

    def __setitem__(self, key, value):
        tKey, category = self._resolve_key(key)
        getattr(self, category)[tKey] = value
        super().__setitem__(tKey, value)

    def __getitem__(self, key):
        tKey, _ = self._resolve_key(key)
        return super().__getitem__(tKey)

    def _get_val_cat_pair(self, key):
        tKey, cat = self._resolve_key(key)
        return (super().__getitem__(tKey), cat)

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
                key = key[0]
                if key in self:
                    for cat in self.categories:
                        if key in getattr(self, cat):
                            return (key, cat)
                    raise NotImplementedError(f"Error fetching {key}, this is a bug, please report it to GitHub as an issue along with the context")
                else:    
                    return (key, self.defaultCat)
            else:
                raise ValueError(f"too many or no keys found in {key}")
            
        raise ValueError(f"key was given in incorrect format, use string tuple or list")
    
    def pop(self, key):
        tKey, category = self._resolve_key(key)
        getattr(self, category).pop(tKey)
        return super().pop(tKey)
    
    def popitem(self):
        (key, value) = super().popitem
        tKey, category = self._resolve_key(key)
        getattr(self, category).pop(tKey)
        return (key, value)
    
    def populateSelf(self, rawDict:dict, **kwargs):
        """
        Populate category dict object based on a dictionary, as well as mapping of categories to keys

            - rawDict: dictionary with key-value pairs
            - **kwargs: category=keys, where category is the param name and keys is a list of keys belonging to that category
        """
        for cat, keys in kwargs.items():
            if not cat in self.categories:
                raise KeyError(f"category {cat} doesn't exist in {self}")
            for key in keys:
                val = rawDict.pop(key, None)  
                self.__setitem__((key, cat),val)

        if rawDict:
            if not self.defaultCat:
                raise KeyError(f"Unknown keys {rawDict} added to {self} with no default category")
            #adding unknown keys as "optional" or whatever default category is chosen
            logger.warning(f"Unknown keys {rawDict.items()}, adding as {self.defaultCat} values")
            for key,value in rawDict.items():
                self.__setitem__((key, self.defaultCat), value)
        

def main():

    testDict = catDict()
    testDict["tester"] = 1243

    print("hello")
    pass


if __name__ == "__main__":
    main()




