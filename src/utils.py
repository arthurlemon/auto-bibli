from urllib.parse import urlparse, unquote
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def set_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.implicitly_wait(2)
    return driver


def extract_data_from_url(url):
    """
    Extract town, neighborhood, and Centris listing ID from a Centris.ca URL.

    Args:
        url (str): A Centris.ca URL

    Returns:
        dict: A dictionary containing 'town', 'neighborhood', and 'centris_id'
    """
    # Validate URL
    try:
        parsed_url = urlparse(url)

        # Check if it's a Centris.ca URL
        if not parsed_url.netloc.endswith("centris.ca"):
            raise ValueError("Not a Centris.ca URL")

        # Decode the path to handle URL encoding
        path = unquote(parsed_url.path)

        # Extract location and ID from the path
        # The pattern is typically: /fr/property-type~transaction-type~town-neighborhood/listing-id
        match = re.search(r"/fr/[^/]+~[^/]+~([^/]+)/(\d+)", path)

        if not match:
            raise ValueError("Could not parse location from URL")

        # Extract location parts
        location_parts = match.group(1).split("-")

        # Extract Centris ID
        centris_id = match.group(2)

        # Handle different possible formats
        if len(location_parts) > 1:
            # Assuming the first part is town, the rest is neighborhood
            town = location_parts[0].capitalize()
            neighborhood = " ".join(location_parts[1:]).title()
        else:
            town = location_parts[0].capitalize()
            neighborhood = None

        return {"ville": town, "quartier": neighborhood, "centris_id": centris_id}

    except Exception as e:
        print(f"Error parsing URL: {e}")
        return None
