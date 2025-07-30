"""Flipkart scraper implementation for Product Recommender."""

import logging
from typing import Any

import numpy as np
from bs4 import BeautifulSoup

from product_recommender.utils.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Flipkart class variables (replace with actual values in your project)
FlipAllRows = "_75nlfW"

# Width 100% (eg: phone)
FlipWid100Desc = "KzDlHZ"
FlipWid100Prodlnk = "CGtC98"
FlipWid100Pricebox = "Nx9bqj _4b5DiR"
FlipWid100RatingBox = "XQDdHH"
FlipWid100Raters = "Wphh3N"
FlipWid100Imgurl = "DByuf4"

# Width 25%
FlipWid25Pricebox = "Nx9bqj"
FlipWid25Raters = "Wphh3N"

# Width 25% Cat1 -> Rating shown in landing page (eg: trimmer)
FlipWid25Cat1ProdsInRow = "slAVV4"
FlipWid25Cat1Header = "wjcEIp"
FlipWid25Cat1RatingBox = "XQDdHH"
FlipWid25Cat1Imgurl = "DByuf4"

# Width 25% Cat2 -> Rating shown in product page (eg: shoes)
FlipWid25Cat2ProdsInRow = "_1sdMkc LFEi7Z"
FlipWid25Cat2Header = "WKTcLC"
FlipWid25Cat2RatingTab = "ISksQ2"
FlipWid25Cat2RatingBox = "XQDdHH"
FlipWid25Cat2Imgurl = "_53J4C-"


class FlipkartScraper(BaseScraper):
    """Scraper for extracting product data from Flipkart."""

    @property
    def platform_name(self) -> str:
        """Return the platform name 'Flipkart'."""
        return "Flipkart"

    def get_search_url(self, search_term: str, page: int) -> str:
        """Construct the Flipkart search URL for a given term and page."""
        query = search_term.replace(" ", "%20")
        return (
            f"https://www.flipkart.com/search?"
            f"q={query}"
            "&sort=popularity"
            "&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove"
            "&p%5B%5D=facets.fulfilled_by%255B%255D%3DF-Assured"
            f"&page={page}"
        )

    def get_product_cards(self, soup: Any) -> Any:
        """Extract product card elements from the soup."""
        return soup.find_all("div", class_=FlipAllRows)

    def parse_product_card(self, product_card: Any, session: Any = None) -> list[Any]:
        """Parse a single product card and extract product details."""
        style = product_card.find("div")["style"] if product_card.find("div") else ""

        if style == "width:100%":
            return self._parse_style_100(product_card)
        elif style == "width:25%":
            return self._parse_style_25(product_card, session)
        else:
            raise Exception("Width different that 25% or 100%, hence not parseable.")

    def _parse_style_100(self, product_row: Any) -> list[Any]:
        description = product_row.find("div", class_=FlipWid100Desc).text
        product_link = (
            "https://www.flipkart.com"
            + (product_row.find("a", class_=FlipWid100Prodlnk)["href"].split("?")[0])
        )
        price = int(
            product_row.find("div", class_=FlipWid100Pricebox).text[1:].replace(",", "")
        )
        rating = float(product_row.find("div", class_=FlipWid100RatingBox).text)
        rate_data = product_row.find("span", class_=FlipWid100Raters).text.split()
        raters = int(rate_data[0].replace(",", ""))
        if raters < 30:
            return []
        reviewers = int(rate_data[3].replace(",", ""))
        image_url = product_row.find("img", class_=FlipWid100Imgurl)["src"]
        return [
            [
                self.platform_name,
                description,
                product_link,
                price,
                rating,
                raters,
                reviewers,
                image_url,
            ]
        ]

    def _parse_style_25(self, product_row: Any, session: Any) -> list[Any]:
        product_cards_cat1 = product_row.find_all("div", class_=FlipWid25Cat1ProdsInRow)
        parsed_products = []
        if product_cards_cat1:
            parsed_products = self._parse_style_25_cat1(
                product_cards_cat1=product_cards_cat1
            )
        else:
            product_cards_cat2 = product_row.find_all(
                "div", class_=FlipWid25Cat2ProdsInRow
            )
            parsed_products = self._parse_style_25_cat2(
                product_cards_cat2=product_cards_cat2, session=session
            )

        return parsed_products

    def _parse_style_25_cat1(self, product_cards_cat1) -> list[Any]:
        parsed_products = []
        for product_card in product_cards_cat1:
            header = product_card.find("a", class_=FlipWid25Cat1Header)
            description = header["title"]
            product_link = "https://www.flipkart.com" + header["href"].split("?")[0]
            price_box = product_card.find("div", class_=FlipWid25Pricebox)
            if not price_box:
                logger.warning(
                    "Skipping scraping product with url: "
                    f"{product_link} because price data not found."
                )
                continue
            price = int(price_box.text[1:].replace(",", ""))
            rating = float(product_card.find("div", class_=FlipWid25Cat1RatingBox).text)
            raters = int(
                product_card.find("span", class_=FlipWid25Raters)
                .text[1:-1]
                .replace(",", "")
            )
            if raters < 30:
                logger.debug(
                    "Skipping scraping product with url: "
                    f"{product_link} because only {raters} (<30) people have rated it."
                )
                continue
            img_url = product_card.find("img", class_=FlipWid25Cat1Imgurl)["src"]
            parsed_products.append(
                [
                    self.platform_name,
                    description,
                    product_link,
                    price,
                    rating,
                    raters,
                    np.nan,
                    img_url,
                ]
            )
        return parsed_products

    def _parse_style_25_cat2(self, product_cards_cat2: Any, session: Any) -> list[Any]:
        parsed_products = []
        for product_card in product_cards_cat2:
            header = product_card.find("a", class_=FlipWid25Cat2Header)
            description = header["title"]
            product_link = "https://www.flipkart.com" + header["href"].split("?")[0]
            price = int(
                product_card.find("div", class_=FlipWid25Pricebox)
                .text[1:]
                .replace(",", "")
            )

            product_text = session.get(product_link).text
            product_soup = BeautifulSoup(product_text, "html.parser")
            rating_tab = product_soup.find("div", class_=FlipWid25Cat2RatingTab)

            if not rating_tab:
                logger.warning(
                    "Skipping scraping product with url: "
                    f"{product_link} because rating data not found."
                )
                continue

            rating_box = rating_tab.find("div", class_=FlipWid25Cat2RatingBox)  # type: ignore
            raters_data = rating_tab.find("span", class_=FlipWid25Raters)  # type: ignore

            rating = float(rating_box.text)  # type: ignore
            split_data = raters_data.text.split()  # type: ignore
            if len(split_data) < 4:
                logger.warning(
                    f"Skipping scraping product with url: {product_link} "
                    f"because of incorrectly formatted rating information: "
                    f"{raters_data.text}"  # type: ignore
                )
                continue

            raters = int(split_data[0].replace(",", ""))
            if raters < 30:
                logger.debug(
                    f"Skipping scraping product with url: {product_link} "
                    f"because only {raters} (<30) people have rated it."
                )
                continue

            reviewers = int(split_data[3].replace(",", ""))
            image_url = product_card.find("img", class_=FlipWid25Cat2Imgurl)["src"]

            parsed_products.append(
                [
                    self.platform_name,
                    description,
                    product_link,
                    price,
                    rating,
                    raters,
                    reviewers,
                    image_url,
                ]
            )

        return parsed_products
