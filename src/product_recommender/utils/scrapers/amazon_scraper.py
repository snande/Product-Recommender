"""Amazon scraper implementation for Product Recommender."""

import logging
from typing import Any

from product_recommender.utils.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

AmazProdCards = "puis-card-container"
AmazBrand = "a-size-mini s-line-clamp-1"
# eg: smartphone, watch
AmazDesc2Line = (
    "a-link-normal s-line-clamp-2 s-line-clamp-3-for-col-12 s-link-style a-text-normal"
)
# eg: trimmer
AmazDesc3Line = "a-link-normal s-line-clamp-3 s-link-style a-text-normal"
AmazPriceTag = "a-offscreen"
AmazRateTag = "a-row a-size-small"
AmazRatersTag = "a-link-normal s-underline-text s-underline-link-text s-link-style"
AmazImgTag = "s-image"


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
        product_cards = soup.find_all("div", class_=AmazProdCards)
        return product_cards

    def parse_product_card(self, product_card: Any, session: Any = None) -> list[Any]:
        """Parse a single product card and extract product details."""
        brand = product_card.find("h2", class_=AmazBrand)
        brand = brand.text + " | " if brand else ""
        description_box = product_card.find("a", class_=AmazDesc2Line)
        if not description_box:
            description_box = product_card.find("a", class_=AmazDesc3Line)
        description = brand + description_box.text

        product_link = (
            "https://www.amazon.in" + description_box["href"].split("/ref=")[0]
        )
        price_tag = product_card.find("span", class_=AmazPriceTag)
        if not price_tag:
            logger.debug(
                "Skipping scraping product with url: "
                f"{product_link} because price data not found."
            )
            return []
        price = int(round(float(price_tag.text[1:].replace(",", "")), 0))

        rate_tag = product_card.find("div", class_=AmazRateTag)
        raters_tag = product_card.find("a", class_=AmazRatersTag)

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

        image_tag = product_card.find("img", class_=AmazImgTag)
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
