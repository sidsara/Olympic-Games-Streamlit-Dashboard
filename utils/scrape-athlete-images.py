"""
scrape_athlete_images.py
=========================
Fetches athlete image URLs from Wikipedia using the public API.
This script updates athletes_enriched.csv with a new column: image_url.

Run it once before launching the Streamlit app.
"""

import requests
import pandas as pd
from tqdm import tqdm
from pathlib import Path

# Define data directory
DATA_DIR = Path(__file__).parent.parent / "data"
INPUT_FILE = DATA_DIR / "athletes_enriched.csv"
OUTPUT_FILE = DATA_DIR / "athletes_with_images.csv"

def get_wikipedia_image(name):
    """
    Search for an athlete's image on Wikipedia.
    Returns the image URL if found, else None.
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": name
    }

    try:
        res = requests.get(search_url, params=params, timeout=8)
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "original" in page:
                return page["original"]["source"]
    except Exception:
        return None

    return None

def main():
    print("🔍 Loading athlete data...")
    athletes = pd.read_csv(INPUT_FILE)
    if "image_url" not in athletes.columns:
        athletes["image_url"] = None

    print("📸 Fetching images from Wikipedia...")
    for i, name in tqdm(enumerate(athletes["name"]), total=len(athletes)):
        if pd.notna(athletes.at[i, "image_url"]):
            continue  # Skip if already has an image
        image_url = get_wikipedia_image(name)
        athletes.at[i, "image_url"] = image_url

    print("💾 Saving updated dataset...")
    athletes.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Done! Saved as {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
