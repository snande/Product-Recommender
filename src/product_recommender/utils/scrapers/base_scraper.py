"""Base scraper abstract class for Product Recommender."""

import logging
import random
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from product_recommender.utils.helpers import get_html

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all product scrapers."""

    def scrape(
        self,
        search_term: str,
        num_pages: int = 6,
    ) -> pd.DataFrame:
        """Scrape products for a search term using the implemented methods."""
        df_list = self._process_pages_in_parallel(
            search_term=search_term, num_pages=num_pages, num_threads=5
        )
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
                "page",
            ],
        )

    def _get_response_text(self, url: str) -> Any:
        attempts = 1
        start_time = time.time()
        while (time.time() - start_time) < 100:
            response = get_html(url)
            if response.status_code == 200:
                logger.debug(
                    f"Request succeeded after trying {attempts} times for url: {url}"
                )
                return response.text
            logger.warning(f"Request failed at {attempts} attempt for url: {url}")
            delay = random.uniform(0.1, 5.5)
            time.sleep(delay)
            attempts += 1
        logger.error(
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
    def parse_product_card(self, product_card: Any) -> list[Any]:
        """Parse a single product card and extract product details."""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name for the scraper."""
        pass

    def _process_cards_in_parallel(
        self, cards: Any, num_threads: int = 10
    ) -> list[list[Any]]:
        futures = []
        parsed_products: list[list[Any]] = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for card in cards:
                futures.append(executor.submit(self.parse_product_card, card))

            for future in futures:
                if future.result():
                    parsed_products = parsed_products + future.result()
        return parsed_products

    def _process_one_page(self, search_term: str, page: int) -> list[list[Any]] | None:
        logger.info(
            f"Starting scraping for page: {page} on platform {self.platform_name}"
        )
        url = self.get_search_url(search_term, page)
        html = self._get_response_text(url)
        if not html:
            logger.warning(
                f"Skipping crawling url: {url} because of multiple failed attempts."
            )
            return None
        soup = BeautifulSoup(html, "html.parser")
        cards = self.get_product_cards(soup)
        logger.debug(
            f"Found {len(cards)} product cards in\
             page: {page} on platform {self.platform_name}"
        )

        parsed_products = self._process_cards_in_parallel(cards=cards, num_threads=5)
        logger.info(
            f"Found {len(parsed_products)} products\
             on page: {page} for platform: {self.platform_name}"
        )
        parsed_products = [product + [page] for product in parsed_products]
        return parsed_products

    def _process_pages_in_parallel(
        self,
        search_term: str,
        num_pages: int,
        num_threads: int = 10,
    ) -> list[list[Any]]:
        futures = []
        df_list: list[list[Any]] = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for page in range(1, num_pages + 1):
                futures.append(
                    executor.submit(
                        self._process_one_page,
                        search_term=search_term,
                        page=page,
                    )
                )

            for future in futures:
                result = future.result()
                if result is not None:
                    df_list = df_list + result
        return df_list
