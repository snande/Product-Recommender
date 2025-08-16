"""Search service for fetching products and handling cache logic."""

import logging

from pandas import DataFrame

from product_recommender.services.analytics import attach_metrics
from product_recommender.services.cache import get_cached_result, save_to_cache
from product_recommender.services.scraper import get_all_products
from product_recommender.utils.logging import get_logger

logger = get_logger(name="product_recommender", console_log_level=logging.DEBUG)


def fetch_products(search_term: str, force_refresh: bool = False) -> DataFrame:
    """Fetch products for a search term, using cache unless force_refresh is True."""
    search_term = search_term.lower()
    if not force_refresh:
        cached_df = get_cached_result(search_term)
        if cached_df is not None:
            return cached_df

    df_all_products = get_all_products(search_term)
    df = attach_metrics(df_all_products)
    save_to_cache(search_term, df)
    return df
