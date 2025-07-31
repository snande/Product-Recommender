"""Data handler subpackage for Product Recommender."""

from .loader import load_key_dict, load_result_file
from .saver import save_key_dict, save_result_file
from .storage import get_blob_client, get_container_client

__all__ = [
    "load_key_dict",
    "load_result_file",
    "get_blob_client",
    "get_container_client",
    "save_key_dict",
    "save_result_file",
]
