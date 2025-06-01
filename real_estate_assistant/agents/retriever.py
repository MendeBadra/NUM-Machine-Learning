import io
import re

import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup


class RetrieverAgent:
    def __init__(self):
        pass

    def fetch_listing_data(self, url: str) -> str:
        print(f"RetrieverAgent: Fetching content from {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return f"Error: Could not retrieve content from {url}."
        except Exception as e:
            print(f"An unexpected error occurred while fetching {url}: {e}")
            return f"Error: An unexpected error occurred while retrieving content from {url}."

    def fetch_statistical_data(self, url: str) -> str:
        print(f"RetrieverAgent: Fetching content from {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return f"Error: Could not retrieve content from {url}."
        except Exception as e:
            print(f"An unexpected error occurred while fetching {url}: {e}")
            return f"Error: An unexpected error occurred while retrieving content from {url}."

    def extract_listing_details(self, url: str) -> dict:
        print(f"RetrieverAgent: Extracting details from {url}")
        html_content = self.fetch_listing_data(url)
        if html_content.startswith("Error:"):
            return {
                "url": url,
                "title": "Error fetching page",
                "price": "N/A",
                "location": "N/A",
                "area": "N/A",
                "rooms": "N/A",
                "description": "N/A",
                "error": html_content
            }

        soup = BeautifulSoup(html_content, 'lxml')

        details = {
            "url": url,
            "title": "N/A",
            "price": "N/A",
            "location": "N/A",
            "area": "N/A",
            "rooms": "N/A",
            "description": "N/A"
        }

        title_tag = soup.find('h1')
        if title_tag:
            details['title'] = title_tag.text.strip()
        else:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                details['title'] = og_title['content'].strip()

        price_container = soup.find('section', class_='list-announcement')
        if price_container and price_container.has_attr('data-price'):
            try:
                price = float(price_container['data-price'])
                details['price'] = f"MNT {price:,.0f}"
            except ValueError:
                details['price'] = price_container['data-price']
        else:
            price_tag = soup.find(class_='announcement-price__value')
            if price_tag:
                details['price'] = price_tag.get_text(strip=True)

        location_tag = soup.find(string=lambda t: t and ("байршил" in t.lower() or "location" in t.lower()))
        if location_tag:
            parent = location_tag.find_parent()
            if parent:
                details['location'] = parent.text.strip().replace('\n', ' ').replace('\r', '').replace('\t', ' ')
            else:
                details['location'] = location_tag.strip()

        area_li = soup.find('span', string=lambda t: t and 'талбай' in t.lower())
        if area_li:
            parent_li = area_li.find_parent('li')
            if parent_li:
                value_tag = parent_li.find('a', class_='value-chars')
                if value_tag:
                    details['area'] = value_tag.text.strip()

        bedrooms_tag = soup.find(string=lambda t: t and ("өрөө" in t.lower() or "rooms" in t.lower()))
        if bedrooms_tag:
            details['rooms'] = bedrooms_tag.strip()

        description_tag = soup.find('div', class_='announcement-description')
        if description_tag:
            details['description'] = description_tag.text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        else:
            og_description = soup.find('meta', property='og:description')
            if og_description and og_description.get('content'):
                details['description'] = og_description['content'].strip()
            else:
                body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ""
                details['description'] = (body_text[:500] + '...') if len(body_text) > 500 else body_text

        print(f"RetrieverAgent: Extracted details: {details}")
        return details

    def extract_statistical_data_from_1212(self, district="Баянзүрх") -> dict:
        print(f"RetrieverAgent: Extracting apartment stats for {district}")
        stats_url = "https://1212.mn/stat.aspx?LIST_ID=976_L4_B1"  # Example: change as needed
        html_content = self.fetch_statistical_data(stats_url)

        if html_content.startswith("Error:"):
            return {"district": district, "error": html_content}

        soup = BeautifulSoup(html_content, "lxml")

        stats = {
            "district": district,
            "new_apartment_price": "N/A",
            "old_apartment_price": "N/A"
        }

        try:
            table = soup.find("table")
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)

                    if "шинэ" in label and district in label:
                        stats["new_apartment_price"] = value
                    elif "хуучин" in label and district in label:
                        stats["old_apartment_price"] = value
        except Exception as e:
            stats["error"] = f"Failed to parse 1212.mn: {e}"

        return stats

    def search_general_listings(self, location: str, property_type: str, **kwargs) -> list:
        print(f"RetrieverAgent: Searching for {property_type} in {location} with criteria {kwargs}")
        return [
            {"source": "mock", "title": f"Sample {property_type} in {location} 1", "price": "MNT 100,000,000", "url": "http://example.com/1"},
            {"source": "mock", "title": f"Sample {property_type} in {location} 2", "price": "MNT 120,000,000", "url": "http://example.com/2"}
        ]

    # --- New PDF extraction methods ---

    def extract_table_from_text(self, lines, start_header, end_header):
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

    def parse_price_lines(self, price_lines):
        rows = []
        for line in price_lines:
            parts = re.split(r'\s+', line)
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

    def extract_apartment_price_from_pdf(self, pdf_url: str = None):
        """
        Download and extract apartment price tables (new and old) from the PDF.
        Returns dict with two DataFrames: new and old apartment prices.
        """
        if not pdf_url:
            pdf_url = "https://downloads.1212.mn/JTjvL9z4sDu9E9ro-BcOLaJ_e-VQS_ouZ_BVsiNl.pdf"

        print(f"RetrieverAgent: Downloading PDF from {pdf_url}")
        try:
            r = requests.get(pdf_url, timeout=15)
            r.raise_for_status()
        except Exception as e:
            return {"error": f"Failed to download PDF: {e}"}

        pdf_file = io.BytesIO(r.content)
        with pdfplumber.open(pdf_file) as pdf:
            page2 = pdf.pages[1]
            text = page2.extract_text()
            lines = text.split('\n')

            new_apart_lines = self.extract_table_from_text(
                lines,
                start_header="Average price of new apartment",
                end_header="Average price of old apartment"
            )
            old_apart_lines = self.extract_table_from_text(
                lines,
                start_header="Average price of old apartment",
                end_header="Source: Website"
            )

            new_apart_data = self.parse_price_lines(new_apart_lines)
            old_apart_data = self.parse_price_lines(old_apart_lines)

            df_new = pd.DataFrame(new_apart_data)
            df_old = pd.DataFrame(old_apart_data)
            
            dict={
                "new_apartment_prices": df_new,
                "old_apartment_prices": df_old
            }
            print(dict["new_apartment_prices"])
            print(dict["old_apartment_prices"])
            return dict
            

if __name__ == '__main__':
    retriever = RetrieverAgent()

    # Test: Single listing extraction
    test_url = "https://www.unegui.mn/adv/9129580_tomor-zamd-2-oroo-zarna/"
    print(f"\n--- Testing Single Listing Extraction for: {test_url} ---")
    listing_details = retriever.extract_listing_details(test_url)
    if "error" not in listing_details:
        print("\nSuccessfully extracted details:")
        for key, value in listing_details.items():
            print(f"  {key.capitalize()}: {value}")
    else:
        print(f"\nError during extraction: {listing_details.get('error')}")
        print(f"Partial details: {listing_details}")

    # Test: General search
    print("\n--- Testing General Search ---")
    general_search_results = retriever.search_general_listings(location="Bayanzurkh district", property_type="apartment", bedrooms=2)
    print("\nGeneral Search Results:")
    for item in general_search_results:
        print(item)

    # Test: Apartment prices from PDF
    print("\n--- Testing PDF Apartment Price Extraction ---")
    price_data = retriever.extract_apartment_price_from_pdf()
    if "error" in price_data:
        print("Error:", price_data["error"])
    else:
        print("\nNew Apartment Prices:")
        print(price_data["new_apartment_prices"])
        print("\nOld Apartment Prices:")
        print(price_data["old_apartment_prices"])
