"""Helper functions and headers for Product Recommender."""

import random

import httpx

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
]


def get_html(url: str) -> httpx.Response:
    """Fetch the HTML response for a given URL using a random user agent.

    This function sends a GET request to the specified URL, using a randomly selected
    user agent from a predefined list to help avoid bot detection. It also sets an
    appropriate Referer header based on the domain (Amazon, Flipkart, or default).
    The function returns the httpx.Response object for further processing.

    Args:
        url (str): The URL to fetch.

    Returns:
        httpx.Response: The HTTP response object containing the HTML content.
    """
    base_headers = {"Accept-Language": "en-US,en;q=0.9"}
    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        if "amazon.in" in url:
            referer = "https://www.amazon.in/"
        elif "flipcart.com" in url:
            referer = "https://www.flipkart.com/"
        else:
            referer = "https://www.google.com/"
        client.get(referer, headers=base_headers)

        headers = base_headers.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        headers["Referer"] = referer
        with httpx.Client(
            headers=headers, follow_redirects=True, timeout=30.0
        ) as client:
            resp = client.get(url, headers=headers)
            return resp
