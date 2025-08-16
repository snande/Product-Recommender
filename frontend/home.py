"""Home page for the Product Recommender app."""

import streamlit as st

from product_recommender.display.display_data import display_data
from product_recommender.services.search import fetch_products

search_term = st.text_input("Search for a product:")

if search_term:
    force_refresh = st.button("Refresh")
    search_term = search_term.strip().lower()
    print(f"Started fetching for: {search_term}")
    df = fetch_products(search_term, force_refresh)
    display_data(df)
