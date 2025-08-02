"""Scrapers subpackage for Product Recommender."""

from .amazon_scraper import AmazonConstants, AmazonScraper
from .flipkart_scraper import FlipkartConstants, FlipkartScraper

__all__ = ["AmazonScraper", "FlipkartScraper", "AmazonConstants", "FlipkartConstants"]
