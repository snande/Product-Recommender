"""Search service for fetching products and handling cache logic."""

from product_recommender.services.cache import get_cached_result, save_to_cache
from product_recommender.services.scraper import get_all_products


def fetch_products(
    search_term: str, session: object, force_refresh: bool = False
) -> object:
    """Fetch products for a search term, using cache unless force_refresh is True."""
    cached_df = get_cached_result(search_term)
    if cached_df is not None and not force_refresh:
        return cached_df

    df = get_all_products(search_term, session)
    save_to_cache(search_term, df)
    return df
