"""Scraper service for aggregating products from multiple platforms."""

import pandas as pd
from requests import Session

from product_recommender.utils.scrapers.amazon_scraper import AmazonScraper
from product_recommender.utils.scrapers.flipkart_scraper import FlipkartScraper


def get_all_products(search_term: str, session: Session) -> pd.DataFrame:
    """Get all products from Amazon and Flipkart for a given search term."""
    amazon_scraper = AmazonScraper()
    flipkart_scraper = FlipkartScraper()

    amazon_df = amazon_scraper.scrape(search_term, session, max_pages=6)
    flipkart_df = flipkart_scraper.scrape(search_term, session, max_pages=6)

    df = pd.concat([amazon_df, flipkart_df], ignore_index=True)

    return df
