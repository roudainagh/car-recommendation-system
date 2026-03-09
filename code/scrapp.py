import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import os

BASE_URL = "https://www.automobile.tn"
HEADERS = {"User-Agent": "Mozilla/5.0"} # Pretend to be a browser so the site doesn’t block us


# ------------------------------- # SCRAPE BRANDS # -------------------------------
def scrape_brands():

    # Request the main "new cars" page
    soup = BeautifulSoup(
        requests.get(BASE_URL + "/fr/neuf", headers=HEADERS).text,
        "html.parser"
    )

    brands = []
    container = soup.find("div", class_="brands-list") # Find the section listing brands

    # Loop through all brand links
    for a in container.find_all("a", href=True):
        href = a["href"]

        # Only keep links that match the brand pattern
        if "/fr/neuf/" in href and href.count("/") == 3:
            brands.append({
                "brand": href.split("/")[-1].title(), # Extract brand name from URL
                "url": BASE_URL + href                # Full URL to brand page
            })

    print("Brands:", len(brands))
    return brands



# ------------------------------- # SCRAPE MODELS (pages modèles) # -------------------------------
def scrape_models_pages(brand):

    # Request the brand page
    soup = BeautifulSoup(
        requests.get(brand["url"], headers=HEADERS).text,
        "html.parser"
    )

    models = []

    # Each model is inside a "versions-item" block
    for item in soup.find_all("div", class_="versions-item"):

        a = item.find("a", href=True)
        if not a:
            continue

        model_name = item.find("h2").get_text(strip=True)

        models.append({
            "brand": brand["brand"],
            "model": model_name,
            "model_page": BASE_URL + a["href"] # Link to model page
        })

    return models


# ------------------------------- # SCRAPE VERSIONS OF A MODEL # -------------------------------
def scrape_versions(model):

    soup = BeautifulSoup(
        requests.get(model["model_page"], headers=HEADERS).text,
        "html.parser"
    )

    versions = []

    table = soup.find("table", class_="versions") # Table listing versions

    if not table:
        versions.append({
            **model,
            "version": model["model"],
            "version_url": model["model_page"],
            "price": ""
        })
        return versions

    rows = table.find("tbody").find_all("tr")


    for row in rows:
        # If no table, treat the model itself as a single version
        vlink = row.find("td", class_="version").find("a")
        version_name = vlink.get_text(strip=True)
        version_url = BASE_URL + vlink["href"]

        price_td = row.find("td", class_="price")
        price = price_td.get_text(" ", strip=True) if price_td else ""

        versions.append({
            **model,
            "version": version_name,
            "version_url": version_url,
            "price": price
        })

    return versions



# ------------------------------- # SCRAPE SPECS FOR A VERSION # -------------------------------
def scrape_specs(version):

    soup = BeautifulSoup(
        requests.get(version["version_url"], headers=HEADERS).text,
        "html.parser"
    )

    specs_block = soup.find("div", class_="technical-details")

    specs = {}

    if not specs_block:
        return specs

    # Loop through spec tables (engine, dimensions, etc.)
    for table in specs_block.find_all("table"):

        category = table.find("thead").get_text(strip=True)

        for row in table.find_all("tr"):

            th = row.find("th")
            td = row.find("td")

            if not th or not td:
                continue

            key = th.get_text(strip=True)
            value = td.get_text(" ", strip=True) or "Oui"

            # Normalize column name (lowercase, underscores)
            col = f"{category}_{key}".lower()
            col = col.replace(" ", "_").replace("-", "_").replace("/", "_")

            specs[col] = value

    return specs



# ------------------------------- # FULL PIPELINE # -------------------------------
def scrape_all():

    rows = []

    brands = scrape_brands()

    for brand in brands:

        print("\nBrand:", brand["brand"])
        models = scrape_models_pages(brand)

        for model in models:

            versions = scrape_versions(model)

            for version in versions:

                print("  Version:", version["version"])

                specs = scrape_specs(version)

                # Merge version info + specs + scrape date
                row = {
                    **version,
                    **specs,
                    "scraped_date": datetime.now()
                }

                rows.append(row)

                time.sleep(1) # Pause to avoid overloading the server

    return pd.DataFrame(rows)


# ------------------------------- # MAIN EXECUTION # -------------------------------
if __name__ == "__main__":

    df = scrape_all()

    os.makedirs("data", exist_ok=True)
    df.to_csv("cars_versions_specs.csv", index=False)

    print("\n DONE")
    print("Rows:", len(df))
