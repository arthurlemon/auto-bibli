import requests
from typing import List, Dict, Any
import time


class CentrisAPIClient:
    """Client for directly querying Centris property listings API"""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.centris.ca"
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://www.centris.ca",
            "Referer": "https://www.centris.ca/fr/plex~a-vendre~montreal?view=Thumbnail",
            "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

    def get_listings(self, page: int = 1) -> List[Dict[Any, Any]]:
        """
        Get property listings using the Centris API

        Args:
            page: Page number to fetch

        Returns:
            List of property listings
        """
        endpoint = f"{self.base_url}/Property/GetInscriptions"

        payload = {
            "startPosition": (page - 1) * 20,  # 12 items per page
            "maxResults": 20,
            "typeIds": [5],  # Type 5 appears to be for plexes
            "category": "Residential",
            # "sort": [{"field": "Price", "order": "desc"}],
            # "includeFields": [
            #     "Permalink",
            #     "ListingId",
            #     "Category",
            #     "TypeId",
            #     "Address",
            #     "Price"
            # ]
        }

        try:
            response = self.session.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            # save html
            with open(f"page_{page}.html", "w") as f:
                f.write(response.json()["d"]["Result"]["html"])
            return response.json()["d"]["Result"]["html"]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching listings: {e}")
            return []

    def get_all_listings(self, max_pages: int = 5) -> List[Dict[Any, Any]]:
        """
        Get all listings across multiple pages

        Args:
            max_pages: Maximum number of pages to fetch

        Returns:
            List of all property listings
        """
        all_listings = []

        for page in range(1, max_pages + 1):
            listings = self.get_listings(page)
            if not listings:
                break

            all_listings.extend(listings)
            print(f"Fetched {len(listings)} listings from page {page}")

            # Add a small delay between requests
            time.sleep(1)

        return all_listings


# Example usage
def main():
    client = CentrisAPIClient()
    listings = client.get_all_listings(max_pages=1)

    print(f"\nTotal listings fetched: {len(listings)}")


if __name__ == "__main__":
    main()
