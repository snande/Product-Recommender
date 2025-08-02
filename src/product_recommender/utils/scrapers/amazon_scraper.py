"""Amazon scraper implementation for Product Recommender."""

import logging
from typing import Any

from product_recommender.utils.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AmazonConstants:
    """Contants used by Amazon scraper."""

    prod_cards = "puis-card-container"
    brand = "a-size-mini s-line-clamp-1"
    desc_box = "s-line-clamp"
    price_tag = "a-offscreen"
    rate_tag = "a-row a-size-small"
    raters_tag = "a-link-normal s-underline-text s-underline-link-text s-link-style"
    img_tag = "s-image"


class AmazonScraper(BaseScraper):
    """Scraper for extracting product data from Amazon."""

    @property
    def platform_name(self) -> str:
        """Return the platform name 'Amazon'."""
        return "Amazon"

    def get_search_url(self, search_term: str, page: int) -> str:
        """Construct the Amazon search URL for a given term and page."""
        search_for = search_term.replace(" ", "+")
        return (
            f"https://www.amazon.in/s?k={search_for}&rh=p_72%3A1318476031&page={page}"
        )

    def get_product_cards(self, soup: Any) -> Any:
        """Extract product card elements from the soup."""
        product_cards = soup.find_all("div", class_=AmazonConstants.prod_cards)
        return product_cards

    def parse_product_card(self, product_card: Any, session: Any = None) -> list[Any]:
        """Parse a single product card and extract product details."""
        brand = product_card.find("h2", class_=AmazonConstants.brand)
        brand = brand.text + " | " if brand else ""
        description_box = [
            i
            for i in product_card.find_all("a")
            if AmazonConstants.desc_box in "".join(i["class"])
        ][0]
        if not description_box:
            raise Exception("Description box not found.")
        description = brand + description_box.text

        product_link = (
            "https://www.amazon.in" + description_box["href"].split("/ref=")[0]
        )
        price_tag = product_card.find("span", class_=AmazonConstants.price_tag)
        if not price_tag:
            logger.debug(
                "Skipping scraping product with url: "
                f"{product_link} because price data not found."
            )
            return []
        price = int(round(float(price_tag.text[1:].replace(",", "")), 0))

        rate_tag = product_card.find("div", class_=AmazonConstants.rate_tag)
        raters_tag = product_card.find("a", class_=AmazonConstants.raters_tag)

        if not rate_tag or not raters_tag:
            logger.debug(
                f"Skipping scraping product with url: "
                f"{product_link} because rating data not found."
            )
            return []

        rating = float(rate_tag.text[:3])
        raters = (
            raters_tag.text.strip().replace(",", "").replace("(", "").replace(")", "")
        )
        if raters.endswith("K"):
            raters = float(raters[:-1]) * 1000
        raters = int(raters)
        if raters < 30:
            logger.debug(
                "Skipping scraping product with url: "
                f"{product_link} because only {raters} (<30) people have rated it."
            )
            return []

        image_tag = product_card.find("img", class_=AmazonConstants.img_tag)
        image_url = image_tag["src"] if image_tag else None

        return [
            [
                self.platform_name,
                description,
                product_link,
                price,
                rating,
                raters,
                None,
                image_url,
            ]
        ]
