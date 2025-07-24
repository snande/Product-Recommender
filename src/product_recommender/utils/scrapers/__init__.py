"""Scrapers subpackage for Product Recommender."""

from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper

__all__ = ["AmazonScraper", "FlipkartScraper"]
