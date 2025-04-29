
try:
    from importlib.metadata import version

    __version__ = version("mne")
except Exception:
    __version__ = "0.0.0"

from wrapBIDS.Modules import *

__all__ = ["BidsDataset"]