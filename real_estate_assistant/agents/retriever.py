# real_estate_assistant/agents/retriever.py
import requests
from bs4 import BeautifulSoup # Example for parsing HTML

class RetrieverAgent:
    def __init__(self):
        pass

    def fetch_listing_data(self, url: str) -> str:
        """
        Fetches the raw HTML content from a given real estate listing URL.
        """
        print(f"RetrieverAgent: Fetching content from {url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return f"Error: Could not retrieve content from {url}."
        except Exception as e:
            print(f"An unexpected error occurred while fetching {url}: {e}")
            return f"Error: An unexpected error occurred while retrieving content from {url}."

    def extract_listing_details(self, url: str) -> dict:
        """
        Fetches and extracts structured details from a single listing URL.
        Note: Selectors are generic and may need adjustment for specific websites.
        """
        print(f"RetrieverAgent: Extracting details from {url}")
        html_content = self.fetch_listing_data(url)
        if html_content.startswith("Error:"):
            return {
                "url": url,
                "title": "Error fetching page",
                "price": "N/A",
                "location": "N/A",
                "area": "N/A",
                "bedrooms": "N/A",
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
            "bedrooms": "N/A",
            "description": "N/A"
        }

        # Attempt to extract title (common tags: h1, h2, or specific meta tags)
        title_tag = soup.find('h1')
        if title_tag:
            details['title'] = title_tag.text.strip()
        else:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                details['title'] = og_title['content'].strip()

        # Attempt to extract price from data-price attribute
        price_container = soup.find('section', class_='list-announcement')
        if price_container and price_container.has_attr('data-price'):
            try:
                price = float(price_container['data-price'])
                details['price'] = f"MNT {price:,.0f}"  # formatted with commas
            except ValueError:
                details['price'] = price_container['data-price']
        else:
            # fallback extraction methods
            price_tag = soup.find(class_='announcement-price__value')
            if price_tag:
                details['price'] = price_tag.get_text(strip=True)

        
        # Attempt to extract location
        location_tag = soup.find(string=lambda t: t and ("байршил" in t.lower() or "location" in t.lower()))
        if location_tag:
            parent_for_location = location_tag.find_parent()  # Removed the incorrect 'limit' argument
            if parent_for_location:
                details['location'] = parent_for_location.text.strip().replace('\n', ' ').replace('\r', '').replace('\t', ' ')
            else:
                details['location'] = location_tag.strip()

        # Attempt to extract area
        # Attempt to extract area using label-value pattern
        area_li = soup.find('span', string=lambda t: t and 'талбай' in t.lower())
        if area_li:
            parent_li = area_li.find_parent('li')
            if parent_li:
                value_tag = parent_li.find('a', class_='value-chars')
                if value_tag:
                    details['area'] = value_tag.text.strip()


        # Attempt to extract bedrooms
        bedrooms_tag = soup.find(string=lambda t: t and ("өрөө" in t.lower() or "bedroom" in t.lower()))
        if bedrooms_tag:
            details['bedrooms'] = bedrooms_tag.strip()

        # Attempt to extract description
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

    def search_general_listings(self, location: str, property_type: str, **kwargs) -> list:
        """
        Searches for listings based on general criteria.
        This would likely involve interacting with APIs or performing web scraping
        on sites like unegui.mn or 1212.mn.
        (Placeholder)
        """
        print(f"RetrieverAgent: Searching for {property_type} in {location} with criteria {kwargs}")
        return [
            {"source": "mock", "title": f"Sample {property_type} in {location} 1", "price": "MNT 100,000,000", "url": "http://example.com/1"},
            {"source": "mock", "title": f"Sample {property_type} in {location} 2", "price": "MNT 120,000,000", "url": "http://example.com/2"}
        ]

if __name__ == '__main__':
    retriever = RetrieverAgent()
    
    # Test fetching and extracting details from a specific listing
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

    # Test general search
    print("\n--- Testing General Search ---")
    general_search_results = retriever.search_general_listings(location="Bayanzurkh district", property_type="apartment", bedrooms=2)
    print("\nGeneral Search Results:")
    for item in general_search_results:
        print(item)
