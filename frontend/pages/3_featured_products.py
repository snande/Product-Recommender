"""Featured products page for the Product Recommender app."""

import logging
from io import BytesIO
from typing import Any

import numpy as np
import pandas as pd
import requests
import streamlit as st
from azure.storage.blob import BlobServiceClient
from PIL import Image


def safe_float(val: Any) -> float:
    """Safely convert a value to float, returning 0.0 on failure."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def display_data(
    df_rat: pd.DataFrame, df_vfm: pd.DataFrame, df_com: pd.DataFrame
) -> None:
    """Display the data for rated, value for money, and composite products."""
    df_rat = df_rat.sample(10, weights="Scaled Rating")
    df_vfm = df_vfm.sample(10, weights="VFM")
    df_com = df_com.sample(10, weights="composite")

    tab1, tab2, tab3 = st.tabs(
        [
            "Best Products by Rating",
            "Best Products by Value for Money",
            "Best Products by Composite Rating",
        ]
    )

    with tab1:
        df_rat = df_rat.copy()
        df_rat.iloc[:, 8] = df_rat.iloc[:, 8].astype(float)
        df_rat.iloc[:, 9] = df_rat.iloc[:, 9].astype(float)
        df_rat.iloc[:, 10] = df_rat.iloc[:, 10].astype(float)
        for row_index in range(len(df_rat)):
            col1, col2 = st.columns([4, 1])
            col1.write(
                f"{row_index + 1}. "
                f"[{df_rat.iloc[row_index, 1]}]({df_rat.iloc[row_index, 2]})\n"
                f"  **Platform** : {df_rat.iloc[row_index, 0]}\n"
                f"  **Price** : {df_rat.iloc[row_index, 3]} Rs.\n"
                f"  **Rating** : {round(safe_float(df_rat.iloc[row_index, 8]), 2)}\n"
                f"  **Value for Money** : "
                f"{round(safe_float(df_rat.iloc[row_index, 9]), 2)}\n"
                f"  **Composite Rating** : "
                f"{round(safe_float(df_rat.iloc[row_index, 10]), 2)}"
            )
            image_response = requests.get(str(df_rat.iloc[row_index, 7]))
            img_rat: Image.Image = Image.open(BytesIO(image_response.content))
            width, height = img_rat.size
            resize_len = width if width >= height else height
            img_rat = img_rat.resize((resize_len, resize_len))
            col2.image(img_rat)

    with tab2:
        df_vfm = df_vfm.copy()
        df_vfm.iloc[:, 8] = df_vfm.iloc[:, 8].astype(float)
        df_vfm.iloc[:, 9] = df_vfm.iloc[:, 9].astype(float)
        df_vfm.iloc[:, 10] = df_vfm.iloc[:, 10].astype(float)
        for row_index in range(len(df_vfm)):
            col1, col2 = st.columns([4, 1])
            col1.write(
                f"{row_index + 1}. "
                f"[{df_vfm.iloc[row_index, 1]}]({df_vfm.iloc[row_index, 2]})\n"
                f"  **Platform** : {df_vfm.iloc[row_index, 0]}\n"
                f"  **Price** : {df_vfm.iloc[row_index, 3]} Rs.\n"
                f"  **Rating** : {round(safe_float(df_vfm.iloc[row_index, 8]), 2)}\n"
                f"  **Value for Money** : "
                f"{round(safe_float(df_vfm.iloc[row_index, 9]), 2)}\n"
                f"  **Composite Rating** : "
                f"{round(safe_float(df_vfm.iloc[row_index, 10]), 2)}"
            )
            image_response = requests.get(str(df_vfm.iloc[row_index, 7]))
            img_vfm: Image.Image = Image.open(BytesIO(image_response.content))
            width, height = img_vfm.size
            resize_len = width if width >= height else height
            img_vfm = img_vfm.resize((resize_len, resize_len))
            col2.image(img_vfm)

    with tab3:
        df_com = df_com.copy()
        df_com.iloc[:, 8] = df_com.iloc[:, 8].astype(float)
        df_com.iloc[:, 9] = df_com.iloc[:, 9].astype(float)
        df_com.iloc[:, 10] = df_com.iloc[:, 10].astype(float)
        for row_index in range(len(df_com)):
            col1, col2 = st.columns([4, 1])
            col1.write(
                f"{row_index + 1}. "
                f"[{df_com.iloc[row_index, 1]}]({df_com.iloc[row_index, 2]})\n"
                f"  **Platform** : {df_com.iloc[row_index, 0]}\n"
                f"  **Price** : {df_com.iloc[row_index, 3]} Rs.\n"
                f"  **Rating** : {round(safe_float(df_com.iloc[row_index, 8]), 2)}\n"
                f"  **Value for Money** : "
                f"{round(safe_float(df_com.iloc[row_index, 9]), 2)}\n"
                f"  **Composite Rating** : "
                f"{round(safe_float(df_com.iloc[row_index, 10]), 2)}"
            )
            image_response = requests.get(str(df_com.iloc[row_index, 7]))
            img_com: Image.Image = Image.open(BytesIO(image_response.content))
            width, height = img_com.size
            resize_len = width if width >= height else height
            img_com = img_com.resize((resize_len, resize_len))
            col2.image(img_com)


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
key_list = keydict.drop_duplicates(subset=["Search"]).loc[:, "Key"].values
key_list_int = [int(key.split("_")[0]) for key in key_list]
result_file_name = "projects/productRecommendor/data/store/config.json"
last_date = container_client.download_blob(result_file_name).readall()
new_key_list = [
    key_tuple[0]
    for key_tuple in zip(key_list, key_list_int, strict=False)
    if key_tuple[1] > int(last_date)
]

file_name = "projects/productRecommendor/data/store/data_rat.json"
download_data = container_client.download_blob(file_name).readall()
df_rat = pd.read_json(
    BytesIO(download_data),
    dtype={
        "platform": str,
        "Desc": str,
        "Link": str,
        "Price": int,
        "Rating": float,
        "Raters": int,
        "Reviewers": int,
        "img_url": str,
        "Scaled Rating": float,
        "VFM": float,
        "composite": float,
    },
)

file_name = "projects/productRecommendor/data/store/data_vfm.json"
download_data = container_client.download_blob(file_name).readall()
df_vfm = pd.read_json(
    BytesIO(download_data),
    dtype={
        "platform": str,
        "Desc": str,
        "Link": str,
        "Price": int,
        "Rating": float,
        "Raters": int,
        "Reviewers": int,
        "img_url": str,
        "Scaled Rating": float,
        "VFM": float,
        "composite": float,
    },
)

file_name = "projects/productRecommendor/data/store/data_com.json"
download_data = container_client.download_blob(file_name).readall()
df_com = pd.read_json(
    BytesIO(download_data),
    dtype={
        "platform": str,
        "Desc": str,
        "Link": str,
        "Price": int,
        "Rating": float,
        "Raters": int,
        "Reviewers": int,
        "img_url": str,
        "Scaled Rating": float,
        "VFM": float,
        "composite": float,
    },
)


if len(new_key_list) > 0:
    df = pd.DataFrame(
        columns=[
            "platform",
            "Desc",
            "Link",
            "Price",
            "Rating",
            "Raters",
            "Reviewers",
            "img_url",
        ]
    )
    for key in new_key_list:
        result_file_name = "projects/productRecommendor/data/result/" + key + ".json"
        download_data = container_client.download_blob(result_file_name).readall()
        df_ = pd.read_json(
            BytesIO(download_data),
            dtype={
                "platform": str,
                "Desc": str,
                "Link": str,
                "Price": int,
                "Rating": float,
                "Raters": int,
                "Reviewers": int,
                "img_url": str,
                "Scaled Rating": float,
                "VFM": float,
                "composite": float,
            },
        )
        df = pd.concat([df, df_])

    df_rat = pd.concat([df_rat, df]).drop_duplicates("Link")
    df_vfm = pd.concat([df_vfm, df]).drop_duplicates("Link")
    df_com = pd.concat([df_com, df]).drop_duplicates("Link")

    df_rat = (
        df_rat.sort_values(
            ["Scaled Rating", "composite", "VFM", "Raters", "Reviewers"],
            axis=0,
            ascending=False,
        )
        .iloc[:1000]
        .reset_index(drop=True)
    )
    df_vfm = (
        df_vfm.sort_values(
            ["VFM", "composite", "Scaled Rating", "Raters", "Reviewers"],
            axis=0,
            ascending=False,
        )
        .iloc[:1000]
        .reset_index(drop=True)
    )
    df_com = (
        df_com.sort_values(
            ["composite", "Scaled Rating", "VFM", "Raters", "Reviewers"],
            axis=0,
            ascending=False,
        )
        .iloc[:1000]
        .reset_index(drop=True)
    )

    result_file_name = "projects/productRecommendor/data/store/data_rat.json"
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=result_file_name
    )
    _ = blob_client.upload_blob(df_rat.to_json(), overwrite=True)

    result_file_name = "projects/productRecommendor/data/store/data_vfm.json"
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=result_file_name
    )
    _ = blob_client.upload_blob(df_vfm.to_json(), overwrite=True)

    result_file_name = "projects/productRecommendor/data/store/data_com.json"
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=result_file_name
    )
    _ = blob_client.upload_blob(df_com.to_json(), overwrite=True)

    result_file_name = "projects/productRecommendor/data/store/config.json"
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=result_file_name
    )
    _ = blob_client.upload_blob(str(max(key_list_int)), overwrite=True)


if st.button("Refresh"):
    display_data(df_rat, df_vfm, df_com)
    st.stop()

display_data(df_rat, df_vfm, df_com)
