import os
import time
import uuid
import hmac
import hashlib
import base64
import urllib.parse
import requests
import streamlit as st

# Your FatSecret credentials
CONSUMER_KEY = st.secrets.get("FATSECRET_KEY") or os.getenv("FATSECRET_KEY")
CONSUMER_SECRET = st.secrets.get("FATSECRET_SECRET") or os.getenv("FATSECRET_SECRET")

BASE_URL = "https://platform.fatsecret.com/rest/recipes/search/v3"

def percent_encode(s: str) -> str:
    """RFC3986 percent-encode."""
    return urllib.parse.quote(str(s), safe='-._~')

def generate_oauth_signature(http_method: str, url: str, params: dict) -> str:
    """
    1) Percent-encode each key and value.
    2) Sort by key, then by value (lexicographically).
    3) Concatenate into normalized string: k1=v1&k2=v2...
    4) Build signature base string: METHOD&percent_encode(URL)&percent_encode(normalized).
    5) HMAC-SHA1 with key = percent_encode(consumer_secret) + "&"
    6) Base64 encode, then percent-encode the result.
    """
    # 1 & 2
    encoded_pairs = [
        (percent_encode(k), percent_encode(v))
        for k, v in params.items()
    ]
    encoded_pairs.sort()  # lexicographical on (key, value)

    # 3
    normalized = "&".join(f"{k}={v}" for k, v in encoded_pairs)

    # 4
    base_elems = [
        http_method.upper(),
        percent_encode(url),
        percent_encode(normalized)
    ]
    base_string = "&".join(base_elems)

    # 5
    signing_key = percent_encode(CONSUMER_SECRET) + "&"
    digest = hmac.new(
        signing_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha1
    ).digest()

    # 6
    signature = base64.b64encode(digest).decode()
    return percent_encode(signature)

def search_recipes_by_calories(cal_min: int, cal_max: int, max_results: int = 5) -> list:
    """
    Search FatSecret recipes by a calorie range using OAuth1.0.

    Returns a list of dicts: {"id": recipe_id, "name": recipe_name, "url": recipe_url}.
    """
    # Step A: API parameters (method=recipes.search.v3)
    api_params = {
        # "method":            "recipes.search.v3",            # calls the v3 search
        "format":            "json",                         # JSON output
        # "search_expression": "",                             # required, can be blank
        # "calories.from":     str(cal_min),
        # "calories.to":       str(cal_max),
        # "max_results":       str(max_results),
        # "page_number":       "0",
        # "sort_by":           "caloriesPerServingAscending"
    }

    # Step B: OAuth parameters (minus signature)
    oauth_params = {
        "oauth_consumer_key":     CONSUMER_KEY,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        str(int(time.time())),
        "oauth_nonce":            uuid.uuid4().hex,
        "oauth_version":          "1.0"
    }

    # Step C: Combine for signing
    signing_params = {**api_params, **oauth_params}
    oauth_signature = generate_oauth_signature("GET", BASE_URL, signing_params)
    oauth_params["oauth_signature"] = oauth_signature

    # Step D: Final request params = API + OAuth (including signature)
    final_params = {**api_params, **oauth_params}

    # Step E: Send GET request
    resp = requests.get(BASE_URL, params=final_params)
    resp.raise_for_status()
    print(resp.status_code, resp.url)
    print(resp.text)

    # Step F: Parse response
    json_body = resp.json()
    # FatSecret nests recipes under "recipes" → "recipe"
    items = json_body.get("recipes", {}).get("recipe", [])
    if isinstance(items, dict):
        items = [items]

    return [
        {
            "id":   r["recipe_id"],
            "name": r["recipe_name"],
            "url":  r["recipe_url"]
        }
        for r in items
    ]
