import requests
import io
import pdfplumber
import pandas as pd
import re
from bs4 import BeautifulSoup

class RetrieverAgent:
    def __init__(self):
        pass

    # --- unegui.mn specific ---

    def fetch_unegui_page(self, url: str) -> str:
        print(f"Fetching unegui.mn page: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return ""

    def extract_unegui_listing(self, url: str) -> dict:
        """
        Extract details like title, price, location, area, bedrooms, description
        from a single unegui.mn apartment listing page.
        """
        html = self.fetch_unegui_page(url)
        if not html:
            return {"url": url, "error": "Failed to fetch page"}

        soup = BeautifulSoup(html, "lxml")
        details = {"url": url}

        # Title (usually in <h1>)
        title_tag = soup.find("h1")
        details["title"] = title_tag.text.strip() if title_tag else "N/A"

        # Price: look for data-price attribute or price class
        price_section = soup.find("section", class_="list-announcement")
        price = "N/A"
        if price_section and price_section.has_attr("data-price"):
            try:
                price_val = float(price_section["data-price"])
                price = f"MNT {price_val:,.0f}"
            except:
                price = price_section["data-price"]
        else:
            price_tag = soup.find(class_="announcement-price__value")
            if price_tag:
                price = price_tag.text.strip()
        details["price"] = price

        # Location: find by text or meta tag
        loc_tag = soup.find(string=re.compile(r"байршил", re.I))
        if loc_tag:
            loc_parent = loc_tag.find_parent()
            if loc_parent:
                details["location"] = loc_parent.text.strip()
            else:
                details["location"] = loc_tag.strip()
        else:
            details["location"] = "N/A"

        # Area & Bedrooms (usually in list of attributes)
        # Try to find list items containing Talbai (area), Oroo (rooms)
        area = "N/A"
        bedrooms = "N/A"
        for li in soup.find_all("li"):
            text = li.text.lower()
            if "талбай" in text:
                area = li.text.strip()
            if "өрөө" in text:
                bedrooms = li.text.strip()
        details["area"] = area
        details["rooms"] = bedrooms

        # Description
        desc_tag = soup.find("div", class_="announcement-description")
        if desc_tag:
            details["description"] = desc_tag.text.strip()
        else:
            details["description"] = "N/A"

        return details

    # --- 1212.mn statistical data ---

    def fetch_1212_stat_page(self, url: str) -> str:
        print(f"Fetching 1212.mn stats page: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return ""

    def extract_1212_stats(self, url: str, district="Баянзүрх") -> dict:
        """
        Extract apartment price stats from 1212.mn webpage for a given district.
        """
        html = self.fetch_1212_stat_page(url)
        if not html:
            return {"district": district, "error": "Failed to fetch page"}

        soup = BeautifulSoup(html, "lxml")

        stats = {
            "district": district,
            "new_apartment_price": "N/A",
            "old_apartment_price": "N/A"
        }

        try:
            table = soup.find("table")
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                label = tds[0].get_text(strip=True)
                val = tds[1].get_text(strip=True)
                if district in label and "шинэ" in label:
                    stats["new_apartment_price"] = val
                if district in label and "хуучин" in label:
                    stats["old_apartment_price"] = val
        except Exception as e:
            stats["error"] = f"Parse error: {e}"

        return stats

    # --- 1212.mn PDF price table extraction ---

    def extract_table_from_pdf_text(self, lines, start_header, end_header):
        data_lines = []
        inside = False
        for line in lines:
            if start_header in line:
                inside = True
                continue
            if end_header in line and inside:
                break
            if inside and line.strip():
                data_lines.append(line.strip())
        return data_lines

    def parse_price_table_lines(self, lines):
        rows = []
        for line in lines:
            parts = re.split(r"\s+", line)
            if len(parts) < 7:
                continue
            district = parts[0]
            try:
                values = list(map(float, parts[1:7]))
            except ValueError:
                continue
            rows.append({
                "District": district,
                "2025 Mar": values[3],
                "Value": values[4],
                "Percent": values[5],
            })
        return rows

    def extract_apartment_prices_from_pdf(self, pdf_url=None):
        """
        Download PDF from 1212.mn and extract new and old apartment price tables from page 2.
        Returns dict of pandas DataFrames.
        """
        if pdf_url is None:
            pdf_url = "https://downloads.1212.mn/JTjvL9z4sDu9E9ro-BcOLaJ_e-VQS_ouZ_BVsiNl.pdf"
        print(f"Downloading PDF from {pdf_url}")

        try:
            r = requests.get(pdf_url, timeout=15)
            r.raise_for_status()
        except Exception as e:
            return {"error": f"Failed to download PDF: {e}"}

        pdf_file = io.BytesIO(r.content)
        with pdfplumber.open(pdf_file) as pdf:
            page = pdf.pages[1]  # 2nd page (0-based)
            text = page.extract_text()
            lines = text.split('\n')

            new_lines = self.extract_table_from_pdf_text(
                lines,
                "Average price of new apartment",
                "Average price of old apartment"
            )
            old_lines = self.extract_table_from_pdf_text(
                lines,
                "Average price of old apartment",
                "Source:"
            )

            new_df = pd.DataFrame(self.parse_price_table_lines(new_lines))
            old_df = pd.DataFrame(self.parse_price_table_lines(old_lines))

            return {
                "new_apartments": new_df,
                "old_apartments": old_df
            }

# ------------------- USAGE EXAMPLE -------------------

if __name__ == "__main__":
    agent = RetrieverAgent()

    # Extract a listing from unegui.mn
    test_unegui_url = "https://www.unegui.mn/adv/9217777_zaisan-jardin-residence-khotkhond-374-66-mkv-dupleks-7-oroo-bair-khudaldan/"
    print("\n--- Extracting unegui.mn listing ---")
    details = agent.extract_unegui_listing(test_unegui_url)
    for k,v in details.items():
        print(f"{k}: {v}")

    # Extract 1212.mn stats page example
    print("\n--- Extracting 1212.mn stats ---")
    stats_url = "https://1212.mn/stat.aspx?LIST_ID=976_L4_B1"
    stats = agent.extract_1212_stats(stats_url, district="Баянзүрх")
    print(stats)

    # Extract apartment prices from 1212.mn PDF
    print("\n--- Extracting apartment prices from PDF ---")
    pdf_data = agent.extract_apartment_prices_from_pdf()
    if "error" in pdf_data:
        print("PDF Extraction Error:", pdf_data["error"])
    else:
        print("New Apartments Data:")
        print(pdf_data["new_apartments"])
        print("\nOld Apartments Data:")
        print(pdf_data["old_apartments"])
