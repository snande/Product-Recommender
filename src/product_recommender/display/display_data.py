"""Display functions for presenting product data in Product Recommender."""

from io import BytesIO

import pandas as pd
import streamlit as st
from PIL import Image

from product_recommender.utils.helpers import get_html


def display_data(df: pd.DataFrame) -> None:
    """Display product data in a sorted and formatted manner using Streamlit."""
    df_rat = df.sort_values(
        ["scaled_rating", "composite", "vfm", "raters", "reviewers"],
        axis=0,
        ascending=False,
        ignore_index=True,
    ).head(5)
    df_vfm = df.sort_values(
        ["vfm", "composite", "scaled_rating", "raters", "reviewers"],
        axis=0,
        ascending=False,
        ignore_index=True,
    ).head(5)
    df_com = df.sort_values(
        ["composite", "scaled_rating", "vfm", "raters", "reviewers"],
        axis=0,
        ascending=False,
        ignore_index=True,
    ).head(5)

    st.subheader("Best Products by Rating")
    _display_dataframe(df_rat)

    st.subheader("Best Products by Value for Money")
    _display_dataframe(df_vfm)

    st.subheader("Best Products by Composite Rating")
    _display_dataframe(df_com)

    st.subheader("Entire Data Extract")
    st.dataframe(df)


def _display_dataframe(df: pd.DataFrame) -> None:
    for row_index in range(len(df)):
        col1, col2 = st.columns([4, 1])
        col1.write(
            f"""
    {row_index + 1}. [{df.loc[row_index, "description"]}]({df.loc[row_index, "link"]})  
    **Platform** : {df.loc[row_index, "platform"]}  
    **Price** : {df.loc[row_index, "price"]} Rs.  
    **Rating** : {
                round(
                    float(
                        pd.to_numeric(
                            df.loc[row_index, "scaled_rating"], errors="coerce"
                        )
                    ),
                    2,
                )
            }  
    **Value for Money** : {
                round(
                    float(pd.to_numeric(df.loc[row_index, "vfm"], errors="coerce")), 2
                )
            }  
    **Composite Rating** : {
                round(
                    float(
                        pd.to_numeric(df.loc[row_index, "composite"], errors="coerce")
                    ),
                    2,
                )
            }"""  # noqa: W291
        )
        image_url = str(df.loc[row_index, "image_url"])
        image_response = get_html(image_url)
        img: Image.Image = Image.open(BytesIO(image_response.content))
        width, height = img.size
        resize_len = width if width >= height else height
        img = img.resize((resize_len, resize_len))
        col2.image(img)
