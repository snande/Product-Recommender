"""Loader utilities for data handling in Product Recommender."""

from io import BytesIO
from typing import Any

import pandas as pd

from product_recommender.config import AZURE_MASTER_FILE
from product_recommender.data_handler.storage import get_container_client


def load_key_dict() -> Any:
    """Load the key dictionary from the Azure blob storage master file."""
    container_client = get_container_client()
    data = container_client.download_blob(AZURE_MASTER_FILE).readall()
    return pd.read_json(BytesIO(data), dtype={"Search": str, "Time": float, "Key": str})


def load_result_file(filename: str) -> Any:
    """Load a result file from Azure blob storage by filename."""
    container_client = get_container_client()
    data = container_client.download_blob(filename).readall()
    return pd.read_json(BytesIO(data))
