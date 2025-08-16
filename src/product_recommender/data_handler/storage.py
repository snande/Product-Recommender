"""Storage utilities for Azure blob operations in Product Recommender."""

from azure.storage.blob import BlobServiceClient, ContainerClient

from product_recommender.config import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME


def get_blob_client() -> BlobServiceClient:
    """Get a BlobServiceClient instance using the Azure connection string."""
    return BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)


def get_container_client() -> ContainerClient:
    """Get a container client for the configured Azure container name."""
    client = get_blob_client()
    return client.get_container_client(AZURE_CONTAINER_NAME)
