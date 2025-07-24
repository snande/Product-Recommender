"""Base scraper abstract class for Product Recommender."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Abstract base class for all product scrapers."""

    def scrape(
        self,
        search_term: str,
        session: Any,
        max_pages: int = 15,
        ui_hooks: Any = None,
    ) -> Any:
        """Scrape products for a search term using the implemented methods."""
        df_list = []
        product_count = 0
        for page in range(1, max_pages + 1):
            url = self.get_search_url(search_term, page)
            html = self._get_response_text(session, url, ui_hooks, page)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            cards = self.get_product_cards(soup)
            for card in cards:
                product = self.parse_product_card(card, session)
                if product:
                    df_list.append(product)
                    product_count += 1
            if ui_hooks:
                ui_hooks.get("progress", lambda x: None)(
                    min(100, int((product_count / 100) * 100))
                )
            if product_count >= 100:
                break
        if df_list:
            return pd.DataFrame(df_list)
        return None

    def _get_response_text(
        self, session: Any, url: str, ui_hooks: Any, page: int
    ) -> Any:
        attempts = 0
        while attempts < 3:
            response = session.get(url)
            if ui_hooks:
                ui_hooks.get("status", lambda x: None)(
                    f"Attempt {attempts + 1} for page {page},"
                    " status {response.status_code}"
                )
            if response.status_code == 200:
                return response.text
            attempts += 1
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
    def parse_product_card(self, card: Any, session: Any = None) -> Any:
        """Parse a single product card and extract product details."""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name for the scraper."""
        pass
