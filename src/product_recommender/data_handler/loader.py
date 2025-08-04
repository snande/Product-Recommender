"""Loader utilities for data handling in Product Recommender."""

from io import BytesIO

import pandas as pd

from product_recommender.config import AZURE_MASTER_FILE, AZURE_RESULT_FILE_LOC
from product_recommender.data_handler.storage import get_container_client


def load_key_dict() -> pd.DataFrame:
    """Load the key dictionary from the Azure blob storage master file."""
    container_client = get_container_client()
    data = container_client.download_blob(AZURE_MASTER_FILE).readall()
    df = pd.read_json(BytesIO(data), dtype={"search": str, "time": float, "key": str})
    return df


def load_result_file(key: str) -> pd.DataFrame:
    """Load a result file from Azure blob storage by filename."""
    container_client = get_container_client()
    file_path = AZURE_RESULT_FILE_LOC + key + ".json"
    data = container_client.download_blob(file_path).readall()
    df = pd.read_json(BytesIO(data)).round(decimals=3)
    df.columns = [
        "platform",
        "description",
        "link",
        "price",
        "rating",
        "raters",
        "reviewers",
        "image_url",
        "scaled_rating",
        "vfm",
        "composite",
    ]
    return df
