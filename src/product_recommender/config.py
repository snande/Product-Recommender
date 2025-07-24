"""Configuration for the Product Recommender package."""

import streamlit as st

AZURE_CONNECTION_STRING = st.secrets["database_connection"]["connection_string"]
AZURE_CONTAINER_NAME = st.secrets["database_connection"]["container_name"]
AZURE_MASTER_FILE = st.secrets["database_connection"]["masterSearchFileName"]
