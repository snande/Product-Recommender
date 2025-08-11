"""This module provides analytics functions for product recommendation."""

import numpy as np
from pandas import DataFrame


def attach_metrics(df: DataFrame) -> DataFrame:
    """Cleans and augments a product DataFrame with additional metrics for analysis.

    This function performs the following steps:
    1. Removes duplicate rows based on 'price', 'rating', and 'raters'.
    2. Filters products:
        - For 'Amazon', keeps products with 'price'
          between the 2.5th and 98.5th percentiles.
        - Includes all products from 'Flipkart'.
    3. Calculates a 'scaled_rating' by adjusting the
       'rating' based on the number of 'raters'.
    4. Computes a 'vfm' (Value For Money) metric using the scaled_rating and price.
    5. Derives a 'composite' score combining scaled_rating and vfm for further analysis.

    Args:
        df (DataFrame): Input DataFrame containing product data with columns:
            'price', 'rating', 'raters', and 'platform'.

    Returns:
        DataFrame: The processed DataFrame with new columns:
            'scaled_rating', 'vfm', and 'composite'.
    """
    df = df.drop_duplicates(subset=["price", "rating", "raters"])
    if len(df[(df["page"] < 3) & (df["platform"] == "Flipkart")]) > 20:
        df = df[
            (
                (
                    (df["price"] > df.loc[(df["page"] < 3) & (df["platform"] == "Flipkart"), "price"].quantile(0.2))
                    & (df["price"] < df.loc[(df["page"] < 3) & (df["platform"] == "Flipkart"), "platform"].quantile(0.985))
                    & (df["platform"] == "Amazon")
                )
                | (df["platform"] == "Flipkart")
            )
        ]
    df["scaled_rating"] = df["rating"] * (
        1 - np.power(1.25, -1 * np.sqrt(df["raters"].astype(float)))
    )
    df["vfm"] = (
        (df["scaled_rating"] / (df["scaled_rating"].median()))
        * (np.sqrt(df["price"].median()))
        / np.sqrt(df["price"].astype(float))
    )
    df["composite"] = (df["scaled_rating"] / (df["scaled_rating"].median())) * (
        np.sqrt(df["vfm"]) / (np.sqrt(df["vfm"].median()))
    )
    df = df.fillna(np.nan).round(decimals=3).infer_objects(copy=False)
    df["scaled_rating"] = df["scaled_rating"].astype(float).fillna(np.nan)
    df["reviewers"] = df["reviewers"].astype(float).fillna(np.nan)
    return df
