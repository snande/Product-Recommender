"""Storage utilities for Azure blob operations in Product Recommender."""

from typing import Any

from azure.storage.blob import BlobServiceClient

from product_recommender.config import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME


def get_blob_client() -> Any:
    """Get a BlobServiceClient instance using the Azure connection string."""
    return BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)


def get_container_client() -> Any:
    """Get a container client for the configured Azure container name."""
    client = get_blob_client()
    return client.get_container_client(AZURE_CONTAINER_NAME)
