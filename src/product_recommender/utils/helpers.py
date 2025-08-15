"""Helper functions and headers for Product Recommender."""

import requests
from requests.adapters import HTTPAdapter


def create_session() -> requests.Session:
    """Create a requests session with retry logic."""
    session = requests.Session()
    # retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


amazon_headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
    ),
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

flipkart_headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
    ),
    "Referer": "https://www.flipkart.com/",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
        + "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
}
