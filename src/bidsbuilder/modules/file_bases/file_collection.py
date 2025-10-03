from __future__ import annotations

from attrs import define, field
from typing import Union, Any

from ..core.dataset_core import DatasetCore
from ..schema_objects import Entity, Suffix
from ..core.filenames import CompositeFilename
from .directories import Subject, Session

@define(slots=True)
class dataCollection(DatasetCore):
    """
    DATASET COLLECTION:

    AT ITS CORE IT IS:

        RAW DATA
        JSON SIDECAR

    linked data, i.e:
        _channels.tsv
        _events.tsv
        _electrodes.tsv

        etc...
    """
    containers: dict[Any] = field(init=False)
    parent: Union['Subject', 'Session'] = field(init=False, repr=False)

    def __attrs_post_init__(self):
        try:
            self.fetch_object()
        except KeyError as e:
            raise e
        
    @classmethod
    def create(cls, 
                parent:Union[Subject, Session],
                modality:Union[str, None] = None,
                datatype:Union[str, None] = None,
                suffix:Union[str, None] = None,

                entities:Union[dict[str], None] = None,
                metadata:Union[dict[str], None] = None
                ) -> 'dataCollection':
        # ---- process as strings ----
        if suffix == None:
            suffix = datatype

        # ---- conversion to objects ----
        suffix = Suffix(suffix)
        final_ents = dict()
        if entities is not None:
            for key,val in entities.items():
                cur_ent = Entity(key, val)
                #Entity modifies incorrect input keys to correct machine readable version when possible
                #insures the correct name is stored in final dictionary
                final_ents[cur_ent.name] = cur_ent

        t = CompositeFilename(final_ents, suffix=suffix)
        raise NotImplementedError("NEED TO FIX THE DATACOLLECTION IMPORTS")

        dataset = cls(t)
        dataset.populate_metadata(metadata)
        return dataset

    def populate_metadata(self):
        pass

def add_data(*args, **kwargs) -> dataCollection:
    return dataCollection.create(*args, **kwargs)

__all__ = ["add_data"]