"""Cache utilities for Product Recommender."""

import time

from pandas import DataFrame

from product_recommender.data_handler.loader import load_key_dict, load_result_file
from product_recommender.data_handler.saver import save_key_dict, save_result_file


def get_cached_result(search_term: str) -> DataFrame | None:
    """Retrieve cached result for a given search term if available."""
    keydict = load_key_dict()
    entry = keydict[keydict["search"] == search_term]
    if entry.empty:
        return None
    key = entry.iloc[0]["key"]
    return load_result_file(str(key))


def save_to_cache(search_term: str, df: DataFrame) -> None:
    """Save the result DataFrame to cache for a given search term."""
    num_products_amazon = len(df[df["platform"] == "Amazon"])
    num_products_flipkart = len(df[df["platform"] == "Flipkart"])
    saving_time = time.time()
    key = "_".join(
        [
            str(saving_time).split(".")[0],
            str(num_products_amazon),
            str(num_products_flipkart),
        ]
    )
    keydict = load_key_dict()
    keydict.loc[len(keydict), ["search", "time", "key"]] = [
        search_term,
        saving_time,
        key,
    ]
    keydict = keydict.sort_values(["time", "search"], ascending=False)
    save_result_file(key=key, df=df)
    save_key_dict(key_dict_df=keydict)
