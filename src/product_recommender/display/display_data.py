"""Display functions for presenting product data in Product Recommender."""

from io import BytesIO
from typing import Any

import streamlit as st
from PIL import Image


def display_data(df: Any, session: Any) -> None:
    """Display product data in a sorted and formatted manner using Streamlit."""
    df_rat = df.sort_values(
        ["Scaled Rating", "composite", "VFM", "Raters", "Reviewers"],
        axis=0,
        ascending=False,
    ).head(5)
    df_vfm = df.sort_values(
        ["VFM", "composite", "Scaled Rating", "Raters", "Reviewers"],
        axis=0,
        ascending=False,
    ).head(5)
    df_com = df.sort_values(
        ["composite", "Scaled Rating", "VFM", "Raters", "Reviewers"],
        axis=0,
        ascending=False,
    ).head(5)

    st.subheader("Best Products by Rating")
    for row_index in range(len(df_rat)):
        col1, col2 = st.columns([4, 1])
        col1.write(
            f"{row_index + 1}. "
            f"[{df_rat.iloc[row_index, 1]}]({df_rat.iloc[row_index, 2]})\n"
            f"  **Platform** : {df_rat.iloc[row_index, 0]}\n"
            f"  **Price** : {df_rat.iloc[row_index, 3]} Rs.\n"
            f"  **Rating** : {round(df_rat.iloc[row_index, 8], 2)}\n"
            f"  **Value for Money** : "
            f"{round(df_rat.iloc[row_index, 9], 2)}\n"
            f"  **Composite Rating** : "
            f"{round(df_rat.iloc[row_index, 10], 2)}"
        )
        image_response = session.get(df_rat.iloc[row_index, 7])
        img_rat: Image.Image = Image.open(BytesIO(image_response.content))
        width, image_height = img_rat.size
        st.image(img_rat, width=width)

    st.subheader("Best Products by Value for Money")
    for row_index in range(len(df_vfm)):
        col1, col2 = st.columns([4, 1])
        col1.write(
            f"{row_index + 1}. "
            f"[{df_vfm.iloc[row_index, 1]}]({df_vfm.iloc[row_index, 2]})\n"
            f"  **Platform** : {df_vfm.iloc[row_index, 0]}\n"
            f"  **Price** : {df_vfm.iloc[row_index, 3]} Rs.\n"
            f"  **Rating** : {round(df_vfm.iloc[row_index, 8], 2)}\n"
            f"  **Value for Money** : "
            f"{round(df_vfm.iloc[row_index, 9], 2)}\n"
            f"  **Composite Rating** : "
            f"{round(df_vfm.iloc[row_index, 10], 2)}"
        )
        image_response = session.get(df_vfm.iloc[row_index, 7])
        img_vfm: Image.Image = Image.open(BytesIO(image_response.content))
        width, image_height = img_vfm.size
        st.image(
            img_vfm,
            width=200,
        )

    st.subheader("Best Products by Composite Rating")
    for row_index in range(len(df_com)):
        col1, col2 = st.columns([4, 1])
        col1.write(
            f"{row_index + 1}. "
            f"[{df_com.iloc[row_index, 1]}]({df_com.iloc[row_index, 2]})\n"
            f"  **Platform** : {df_com.iloc[row_index, 0]}\n"
            f"  **Price** : {df_com.iloc[row_index, 3]} Rs.\n"
            f"  **Rating** : {round(df_com.iloc[row_index, 8], 2)}\n"
            f"  **Value for Money** : "
            f"{round(df_com.iloc[row_index, 9], 2)}\n"
            f"  **Composite Rating** : "
            f"{round(df_com.iloc[row_index, 10], 2)}"
        )
        image_response = session.get(df_com.iloc[row_index, 7])
        img_com: Image.Image = Image.open(BytesIO(image_response.content))
        width, image_height = img_com.size
        st.image(
            img_com,
            width=200,
        )

    st.subheader("Entire Data Extract")
    st.dataframe(
        df[
            [
                "platform",
                "Desc",
                "Link",
                "Price",
                "Rating",
                "Raters",
                "Reviewers",
                "Scaled Rating",
                "VFM",
                "composite",
            ]
        ]
    )
