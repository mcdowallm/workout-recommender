import os
import streamlit as st
from fatsecret import Fatsecret
import pandas as pd

# Retrieve FatSecret credentials from secrets or environment variables.
FATSECRET_KEY = st.secrets.get("FATSECRET_KEY") or os.getenv("FATSECRET_KEY")
FATSECRET_SECRET = st.secrets.get("FATSECRET_SECRET") or os.getenv("FATSECRET_SECRET")


fs = Fatsecret("9638c53a214b49d2b160e5aae7d66614", "6774cce97ca2413fa8798bf51cbedbdf")
def search_foods(query):
    foods = fs.foods_search(query)
    return foods

