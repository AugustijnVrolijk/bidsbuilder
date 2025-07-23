
try:
    from importlib.metadata import version

    __version__ = version("mne")
except Exception:
    __version__ = "0.0.0"

from .bidsDataset import BidsDataset
__all__ = ["BidsDataset"]