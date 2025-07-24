"""Services subpackage for Product Recommender."""

from .cache import get_cached_result, save_to_cache
from .scraper import get_all_products
from .search import fetch_products

__all__ = ["get_cached_result", "save_to_cache", "get_all_products", "fetch_products"]
