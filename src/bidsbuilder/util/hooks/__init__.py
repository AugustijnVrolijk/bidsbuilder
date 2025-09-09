from .descriptors import HookedDescriptor, DescriptorProtocol
from .containers import *
# DescriptorProtocol protocol is a type that can be used to annote the descriptor
__all__ = ["HookedDescriptor", "DescriptorProtocol", "is_supported_type", "MinimalDict", "MinimalList", "MinimalSet"]
