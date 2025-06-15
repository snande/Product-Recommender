import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import time
from azure.storage.blob import BlobServiceClient
import logging


logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

connection_string = st.secrets["database_connection"]["connection_string"]
container_name = st.secrets["database_connection"]["container_name"]
masterSearchFileName = st.secrets["database_connection"]["masterSearchFileName"]
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container=container_name)

downlodData = container_client.download_blob(masterSearchFileName).readall()
keydict = pd.read_json(BytesIO(downlodData), dtype={"Search":str, "Time":np.float32, "Key":str})

search_for_orig = st.text_input(label='Search for:', value='')

search_for_orig = st.selectbox('or select from:', sorted(keydict["Search"].unique()))

