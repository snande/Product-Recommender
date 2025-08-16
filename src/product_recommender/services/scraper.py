"""Scraper service for aggregating products from multiple platforms."""

from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from product_recommender.utils.scrapers.amazon_scraper import AmazonScraper
from product_recommender.utils.scrapers.flipkart_scraper import FlipkartScraper


def get_all_products(search_term: str) -> pd.DataFrame:
    """Get all products from Amazon and Flipkart for a given search term."""
    amazon_scraper = AmazonScraper()
    flipkart_scraper = FlipkartScraper()

    with ThreadPoolExecutor(max_workers=10) as executor:
        amazon_future = executor.submit(amazon_scraper.scrape, search_term)
        flipkart_future = executor.submit(flipkart_scraper.scrape, search_term)

        amazon_df = amazon_future.result()
        flipkart_df = flipkart_future.result()

    df = pd.concat([amazon_df, flipkart_df], ignore_index=True)

    return df
