import os
import streamlit as st
from fatsecret import Fatsecret
import pandas as pd
from requests_oauthlib import OAuth1
import requests
from oauthlib.oauth1 import SIGNATURE_HMAC  
import time
import uuid
import hmac
import hashlib
import base64
import urllib.parse


# Retrieve FatSecret credentials from secrets or environment variables.
FATSECRET_KEY = st.secrets.get("FATSECRET_KEY") or os.getenv("FATSECRET_KEY")
FATSECRET_SECRET = st.secrets.get("FATSECRET_SECRET") or os.getenv("FATSECRET_SECRET")
BASE_URL         = "https://platform.fatsecret.com/rest/server.api"

def _pct(s: str) -> str:
    return urllib.parse.quote(str(s), safe='-._~')

def _build_sorted_param_string(params: dict) -> str:
    """
    Percent-encode every key & value, then sort lexicographically,
    then join with & into k=v pairs.
    """
    enc_pairs = []
    for k,v in params.items():
        enc_k = _pct(k)
        enc_v = _pct(v)
        enc_pairs.append((enc_k, enc_v))
    enc_pairs.sort()  # lexicographical on (key, value)
    return "&".join(f"{k}={v}" for k,v in enc_pairs)

fs = Fatsecret("9638c53a214b49d2b160e5aae7d66614", "6774cce97ca2413fa8798bf51cbedbdf")
def search_foods(query):
    foods = fs.foods_search(query)
    return foods

def search_recipes_by_calories(cal_min: int, cal_max: int, max_results: int = 5) -> list:
    """
    FatSecret recipes.search.v3 on server.api with manual OAuth1 HMAC‑SHA1
    and fully sorted parameter string (including the trailing '&' on the secret).
    """
    # 1) API parameters (must include method & blank search_expression)
    api_params = {
        "method":             "recipes.search.v3",
        "format":             "json",
        # "search_expression":  "",                 # blank but required
        "calories.from":      str(cal_min),
        "calories.to":        str(cal_max),
        "max_results":        str(max_results),
        "page_number":        "0",
        "sort_by":            "caloriesPerServingAscending",
    }

    # 2) OAuth parameters (no signature yet)
    oauth = {
        "oauth_consumer_key":     FATSECRET_KEY,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        str(int(time.time())),
        "oauth_nonce":            uuid.uuid4().hex,
        "oauth_version":          "1.0"
    }

    # 3) Merge and build the sorted param string
    all_params = {**api_params, **oauth}
    param_str  = _build_sorted_param_string(all_params)

    # 4) Build signature base string
    base_string = "&".join([
        "POST",
        _pct(BASE_URL),
        _pct(param_str)
    ])

    # 5) Sign with HMAC‑SHA1, note the trailing '&'
    key        = _pct(FATSECRET_SECRET)
    digest     = hmac.new(key.encode(), base_string.encode(), hashlib.sha1).digest()
    signature  = base64.b64encode(digest).decode()
    oauth["oauth_signature"] = signature

    # 6) Final POST body = api_params + oauth (including signature)
    post_data = {**api_params, **oauth}

    # 7) Fire the request
    resp = requests.post(BASE_URL, data=post_data)
    # If it still fails, uncomment the next two lines to inspect:
    print(resp.status_code, resp.url)
    print(resp.text)

    # 8) Parse results
    js   = resp.json()
    recs = js.get("recipes", {}).get("recipe", [])
    if isinstance(recs, dict):
        recs = [recs]

    return [
        {"id":   r["recipe_id"],
         "name": r["recipe_name"],
         "url":  r["recipe_url"]}
        for r in recs
    ]