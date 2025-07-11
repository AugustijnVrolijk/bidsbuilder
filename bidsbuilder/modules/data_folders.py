from attrs import define, field
from typing import ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bidsDataset import BidsDataset

@define(slots=True)
class DatasetSubject():
    """
    At the time of writing: 24/06/2025
    Subject needs the following context: 

    required:
      - sessions
    """
    dataset: ClassVar['BidsDataset'] = None
    _n_subjects: ClassVar[int] = 0
    _all_names: ClassVar[set[str]] = set()
    
    _name:str = field(repr=True, default=None, alias="_name")
    number:int = field(repr=False, init=False)
    children:list = field(repr=False, init=False, default=[])
    
    def __attrs_post_init__(self):
        DatasetSubject._n_subjects += 1
        self.number = DatasetSubject._n_subjects
        self._name = self._check_name(self._name)
        DatasetSubject._all_names.add(self._name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val:str|None):
        DatasetSubject._all_names.remove(self._name)
        self._name = self._check_name(val)
        DatasetSubject._all_names.add(self.name)

    def _check_name(self, value):
        if value == None:
            value = str(self.number)

        assert isinstance(value, str), f"Name {value} is of type {type(value)}, expected str"

        if value in DatasetSubject._all_names:
            raise ValueError(f"Duplicate subject name: '{value}' for {self}")

        return value

    def anonymise(self):
        self.name = str(self.number) 

@define(slots=True)
class DatasetSession():
    """
    At the time of writing: 24/06/2025
    Session needs the following context: 

    required:
        - ses_dirs
    """
    pass