"""Flipkart scraper implementation for Product Recommender."""

from typing import Any

import numpy as np
from bs4 import BeautifulSoup

from product_recommender.utils.scrapers.base_scraper import BaseScraper

# Flipkart class variables (replace with actual values in your project)
FlipAllRows = "_1AtVbE col-12-12"
FlipWid100Desc = "_4rR01T"
FlipWid100Prodlnk = "_1fQZEK"
FlipWid100Pricebox = "_30jeq3 _1_WHN1"
FlipWid100Ratebox = "_3LWZlK"
FlipWid100Ratedata = "_2_R_DZ"
FlipWid100Imgurl = "_396cs4 _3exPp9"
FlipWid25Cat1ProdsInRow = "_13oc-S"
FlipWid25Cat1Header = "_1fQZEK"
FlipWid25Cat1Pricebox = "_30jeq3"
FlipWid25Cat1Ratebox = "_3LWZlK"
FlipWid25Cat1Raters = "_2_R_DZ"
FlipWid25Cat1Imgurl = "_396cs4"
FlipWid25Cat2ProdsInRow = "_13oc-S"
FlipWid25Cat2Header = "_1fQZEK"
FlipWid25Cat2Pricebox = "_30jeq3 _1_WHN1"
FlipWid25Cat2Ratebox = "_3LWZlK"
FlipWid25Cat2Imgurl = "_396cs4"


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
            f"https://www.flipkart.com/search?q={query}"
            f"&sort=popularity&p%5B%5D=facets.fulfilled_by%255B%255D%3DPlus%2B%2528FAssured%2529"
            f"&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove"
            f"&p%5B%5D=facets.availability%255B%255D%3DExclude%2BOut%2Bof%2BStock&page={page}"
        )

    def get_product_cards(self, soup: Any) -> Any:
        """Extract product card elements from the soup."""
        return soup.find_all("div", class_=FlipAllRows)

    def parse_product_card(self, product_row: Any, session: Any = None) -> Any:
        """Parse a single product card and extract product details."""
        style = product_row.find("div")["style"] if product_row.find("div") else ""

        if style == "width:100%":
            return self._parse_style_100(product_row)
        elif style == "width:25%":
            return self._parse_style_25(product_row, session)

        return None

    def _parse_style_100(self, product_row: Any) -> list[Any] | None:
        try:
            descrs = product_row.find("div", class_=FlipWid100Desc).text
            prod_link = (
                "https://www.flipkart.com"
                + (
                    product_row.find("a", class_=FlipWid100Prodlnk)["href"].split("?")[
                        0
                    ]
                )
            )
            price = int(
                product_row.find("div", class_=FlipWid100Pricebox)
                .text[1:]
                .replace(",", "")
            )
            rating = float(product_row.find("div", class_=FlipWid100Ratebox).text)
            rate_data = product_row.find("span", class_=FlipWid100Ratedata).text.split()
            raters = int(rate_data[0].replace(",", ""))
            if raters < 30:
                return None
            reviewers = int(rate_data[3].replace(",", ""))
            img_url = product_row.find("img", class_=FlipWid100Imgurl)["src"]
            return [
                self.platform_name,
                descrs,
                prod_link,
                price,
                rating,
                raters,
                reviewers,
                img_url,
            ]
        except Exception:
            return None

    def _parse_style_25(self, product_row: Any, session: Any) -> list[Any] | None:
        product_cards = product_row.find_all("div", class_=FlipWid25Cat1ProdsInRow)
        parsed_products = []

        for product_card in product_cards:
            try:
                header = product_card.find("a", class_=FlipWid25Cat1Header)
                descrs = header["title"]
                prod_link = "https://www.flipkart.com" + header["href"].split("?")[0]
                price = int(
                    product_card.find("div", class_=FlipWid25Cat1Pricebox)
                    .text[1:]
                    .replace(",", "")
                )
                rating = float(
                    product_card.find("div", class_=FlipWid25Cat1Ratebox).text
                )
                raters = int(
                    product_card.find("span", class_=FlipWid25Cat1Raters)
                    .text[1:-1]
                    .replace(",", "")
                )
                if raters < 30:
                    continue
                img_url = product_card.find("img", class_=FlipWid25Cat1Imgurl)["src"]
                parsed_products.append(
                    [
                        self.platform_name,
                        descrs,
                        prod_link,
                        price,
                        rating,
                        raters,
                        np.nan,
                        img_url,
                    ]
                )
            except Exception:
                continue

        if not parsed_products:
            cat2_result = self._parse_style_25_cat2(product_row, session)
            parsed_products = cat2_result if cat2_result is not None else []
        return parsed_products[0] if parsed_products else None

    def _parse_style_25_cat2(self, prod: Any, session: Any) -> list[list[Any]] | None:
        try:
            header = prod.find("a", class_=FlipWid25Cat2Header)
            descrs = header["title"]
            prod_link = "https://www.flipkart.com" + header["href"].split("?")[0]
            price = int(
                prod.find("div", class_=FlipWid25Cat2Pricebox).text[1:].replace(",", "")
            )

            prod_text = session.get(prod_link).text
            prod_soup = BeautifulSoup(prod_text, "html.parser")
            ratebox = prod_soup.find("div", class_=FlipWid25Cat2Ratebox)
            rate_data = prod_soup.find("span", class_=FlipWid25Cat1Raters)

            if not ratebox or not rate_data:
                return None

            rating = float(ratebox.text)
            split_data = rate_data.text.split()
            if len(split_data) < 4:
                return None

            raters = int(split_data[0].replace(",", ""))
            if raters < 30:
                return None

            reviewers = int(split_data[3].replace(",", ""))
            img_url = prod.find("img", class_=FlipWid25Cat2Imgurl)["src"]

            return [
                [
                    self.platform_name,
                    descrs,
                    prod_link,
                    price,
                    rating,
                    raters,
                    reviewers,
                    img_url,
                ]
            ]
        except Exception:
            return None
