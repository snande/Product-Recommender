"""Custom search page for the Product Recommender app."""

import logging
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

connection_string = st.secrets["database_connection"]["connection_string"]
container_name = st.secrets["database_connection"]["container_name"]
master_search_file_name = st.secrets["database_connection"]["masterSearchFileName"]
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container=container_name)

download_data = container_client.download_blob(master_search_file_name).readall()
keydict = pd.read_json(
    BytesIO(download_data), dtype={"Search": str, "Time": np.float32, "Key": str}
)

search_for_orig = st.text_input(label="Search for:", value="")

search_for_orig = st.selectbox("or select from:", sorted(keydict["Search"].unique()))
