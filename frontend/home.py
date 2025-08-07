"""Home page for the Product Recommender app."""

import logging

import streamlit as st

from product_recommender.display.display_data import display_data
from product_recommender.services.search import fetch_products
from product_recommender.utils.helpers import create_session
from product_recommender.utils.logging import get_logger

logger = get_logger(name="product_recommender", console_log_level=logging.DEBUG)

session = create_session()
search_term = st.text_input("Search for a product:")

if search_term:
    force_refresh = st.button("Refresh")
    search_term = search_term.strip().lower()
    logger.info(f"Started fetching for: {search_term}")
    df = fetch_products(search_term, session, force_refresh)
    display_data(df, session)
