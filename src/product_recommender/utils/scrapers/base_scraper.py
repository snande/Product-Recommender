"""Base scraper abstract class for Product Recommender."""

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all product scrapers."""

    def scrape(
        self,
        search_term: str,
        session: requests.Session,
        max_pages: int = 15,
        max_prodcuts: int = 100,
    ) -> pd.DataFrame:
        """Scrape products for a search term using the implemented methods."""
        df_list = []
        product_count = 0
        for page in range(1, max_pages + 1):
            logger.info(f"Starting scraping for page: {page}")
            url = self.get_search_url(search_term, page)
            html = self._get_response_text(session, url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            cards = self.get_product_cards(soup)
            logger.debug(f"Found {len(cards)} product cards in page: {page}")
            products = []
            for card in cards:
                parsed_products: list = self.parse_product_card(card, session)
                if parsed_products:
                    df_list = df_list + parsed_products
                    products += parsed_products
                    product_count += 1
            logger.info(f"Found {len(products)} products on page: {page}")

            if product_count >= max_prodcuts:
                break

        logger.info(f" Found total {len(df_list)} products in {self.platform_name}")

        return pd.DataFrame(
            df_list,
            columns=[
                "platform",
                "description",
                "link",
                "price",
                "rating",
                "raters",
                "reviewers",
                "image_url",
            ],
        )

    def _get_response_text(self, session: requests.Session, url: str) -> Any:
        attempts = 1
        start_time = time.time()
        while (time.time() - start_time) < 100:
            response = session.get(url)
            if response.status_code == 200:
                logger.debug(
                    f"Request succeeded after trying {attempts} times for url: {url}"
                )
                return response.text
            delay = random.uniform(0.1, 5.5)
            time.sleep(delay)
            attempts += 1
        logger.warning(
            f"Request failed even after trying {attempts} times for url: {url}"
        )
        return None

    @abstractmethod
    def get_search_url(self, search_term: str, page: int) -> str:
        """Return the search URL for the given term and page."""
        pass

    @abstractmethod
    def get_product_cards(self, soup: Any) -> Any:
        """Extract product card elements from the soup."""
        pass

    @abstractmethod
    def parse_product_card(
        self, product_card: Any, session: requests.Session | None = None
    ) -> list[Any]:
        """Parse a single product card and extract product details."""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name for the scraper."""
        pass
