"""Home page for the Product Recommender app."""

import streamlit as st

from product_recommender.display.display_data import display_data
from product_recommender.services.search import fetch_products
from product_recommender.utils.helpers import create_session

session = create_session()
search_term = st.text_input("Search for a product:")

if search_term:
    force_refresh = st.button("Refresh")
    search_term = search_term.strip().lower()
    df = fetch_products(search_term, session, force_refresh)
    display_data(df, session)
