"""Amazon scraper implementation for Product Recommender."""

from typing import Any

from product_recommender.utils.scrapers.base_scraper import BaseScraper


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
        product_cards = soup.find_all("div", class_="a-section a-spacing-base")
        if not product_cards:
            product_cards = soup.find_all(
                "div", class_="a-section a-spacing-base a-text-center"
            )
        if not product_cards:
            product_cards = soup.find_all(
                lambda tag: tag.name == "div" and tag.get("class") == ["a-section"]
            )
        return product_cards

    def parse_product_card(self, product_card: Any, session: Any = None) -> Any:
        """Parse a single product card and extract product details."""
        desc_box1 = product_card.find("h5", class_="s-line-clamp-1")
        desc_box2 = product_card.find(
            "span", class_="a-size-base-plus a-color-base a-text-normal"
        )
        desc_box3 = product_card.find(
            "span", class_="a-size-medium a-color-base a-text-normal"
        )

        if not any([desc_box1, desc_box2, desc_box3]):
            return None

        descrs = ""
        if desc_box1:
            descrs += desc_box1.text + " | "
        if desc_box2:
            descrs += desc_box2.text
        if desc_box3:
            descrs += desc_box3.text

        link_tag = product_card.find(
            "a",
            class_=(
                "a-link-normal s-underline-text s-underline-link-text "
                "s-link-style a-text-normal"
            ),
        )
        if not link_tag:
            return None

        prod_link = "https://www.amazon.in" + link_tag["href"].split("/ref=")[0]
        price_tag = product_card.find("span", class_="a-price-whole")
        if not price_tag:
            return None

        rate_tag = product_card.find("span", class_="a-icon-alt")
        raters_tag = product_card.find("span", class_="a-size-base s-underline-text")

        if not rate_tag or not raters_tag:
            return None

        try:
            price = int(round(float(price_tag.text.replace(",", "")), 0))
            rating = float(rate_tag.text.split()[0])
            raters = int(
                raters_tag.text.replace(",", "").replace("(", "").replace(")", "")
            )
            if raters < 30:
                return None

            img_tag = product_card.find("img", class_="s-image")
            img_url = img_tag["src"] if img_tag else None

            return [
                self.platform_name,
                descrs,
                prod_link,
                price,
                rating,
                raters,
                None,
                img_url,
            ]
        except Exception:
            return None
