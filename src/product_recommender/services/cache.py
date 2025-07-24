"""Cache utilities for Product Recommender."""

from product_recommender.data_handler.loader import load_key_dict, load_result_file


def get_cached_result(search_term: str) -> object:
    """Retrieve cached result for a given search term if available."""
    keydict = load_key_dict()
    entry = keydict[keydict["Search"] == search_term]
    if entry.empty:
        return None
    key = entry.iloc[0]["Key"]
    return load_result_file(f"projects/productRecommendor/data/result/{key}.json")


def save_to_cache(search_term: str, df: object) -> None:
    """Save the result DataFrame to cache for a given search term (not implemented)."""
    # Implement if writing to cache is needed
    pass
