"""Search service for fetching products and handling cache logic."""

from requests import Session

from product_recommender.services.analytics import attach_metrics
from product_recommender.services.cache import get_cached_result, save_to_cache
from product_recommender.services.scraper import get_all_products


def fetch_products(
    search_term: str, session: Session, force_refresh: bool = False
) -> object:
    """Fetch products for a search term, using cache unless force_refresh is True."""
    search_term = search_term.lower()
    if not force_refresh:
        cached_df = get_cached_result(search_term)
        if cached_df:
            return cached_df

    df_all_products = get_all_products(search_term, session)
    df = attach_metrics(df_all_products)
    save_to_cache(search_term, df)
    return df
