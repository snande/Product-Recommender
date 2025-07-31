"""Loader utilities for data handling in Product Recommender."""

import pandas as pd

from product_recommender.config import (
    AZURE_CONTAINER_NAME,
    AZURE_MASTER_FILE,
    AZURE_RESULT_FILE_LOC,
)
from product_recommender.data_handler.storage import get_blob_client


def save_key_dict(key_dict_df: pd.DataFrame) -> None:
    """Save the key dictionary from the Azure blob storage master file."""
    container_client = get_blob_client()
    blob_client = container_client.get_blob_client(
        container=AZURE_CONTAINER_NAME, blob=AZURE_MASTER_FILE
    )
    _ = blob_client.upload_blob(key_dict_df.to_json(), overwrite=True)


def save_result_file(key: str, df: pd.DataFrame) -> None:
    """Save a result file to Azure blob storage by filename."""
    container_client = get_blob_client()
    result_file_name = AZURE_RESULT_FILE_LOC + key + ".json"
    blob_client = container_client.get_blob_client(
        container=AZURE_CONTAINER_NAME, blob=result_file_name
    )
    _ = blob_client.upload_blob(df.to_json(), overwrite=True)
