import requests
import re
from selectolax.parser import HTMLParser
from collections import namedtuple
from functools import cached_property
from playwright.sync_api import sync_playwright
from centris.backend.data_models import PlexCentrisListing
from centris.backend.db_models import PlexCentrisListingDB
from centris.backend.mappers import map_bien_centris_to_orm
from datetime import datetime
from loguru import logger


START_URL_PLEX = "https://www.centris.ca/fr/plex~a-vendre~montreal?view=Thumbnail"

UrlData = namedtuple("UrlData", ["centris_id", "ville", "quartier"])


class CentrisBienParser:
    """Extract relevant info data from a parsed HTML of a Centris Duplex listing  page."""

    def __init__(self, url) -> None:
        self.url = url

    def get_data(self, scrape_date: datetime) -> PlexCentrisListing:
        return PlexCentrisListing(
            url=self.url,
            centris_id=self.centris_id,
            title=self.title,
            annee_construction=self.annee_construction,
            description=self.description,
            unites=self.unites,
            nombre_unites=self.nombre_unites,
            superficie_habitable=self.superficie_habitable,
            superficie_batiment=self.superficie_batiment,
            superficie_commerce=self.superficie_commerce,
            superficie_terrain=self.superficie_terrain,
            stationnement=self.stationnement,
            utilisation=self.utilisation,
            adresse=self.addresse,
            ville=self.ville,
            quartier=self.quartier,
            prix=self.prix,
            revenus=self.revenus,
            taxes=self.total_taxes,
            eval_municipale=self.eval_municipale,
            date_scrape=scrape_date.strftime("%Y-%m-%d"),
        )

    def to_db_model(self, scrape_date: str) -> PlexCentrisListingDB:
        data = self.get_data(scrape_date)
        return map_bien_centris_to_orm(data)

    @cached_property
    def html(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch page {self.url}")

        return response.text

    @cached_property
    def tree(self):
        return HTMLParser(self.html)

    @cached_property
    def carac_data(self):
        return self._get_carac_data()

    @cached_property
    def url_data(self) -> UrlData:
        """
        Extracts data from a Centris.ca property URL.

        Args:
            url (str): The Centris.ca URL to parse

        Returns:
            dict: A dictionary containing extracted information
        """

        # Extract property ID from the end of the URL
        match = re.search(r"/fr/[^/]+~[^/]+~([^/]+)/(\d+)", self.url)

        if not match:
            raise ValueError("Could not parse location from URL")

        # Extract location parts
        location_parts = match.group(1).split("-")

        # Extract Centris ID
        centris_id = match.group(2)

        # Handle different possible formats
        if len(location_parts) > 1:
            # Assuming the first part is town, the rest is neighborhood
            ville = location_parts[0].capitalize()
            quartier = " ".join(location_parts[1:]).title()
        else:
            ville = location_parts[0].capitalize()
            quartier = None

        return UrlData(centris_id, ville, quartier)

    @property
    def centris_id(self):
        return int(self.url_data.centris_id)

    @property
    def title(self):
        page_title_span = self.tree.css_first('span[data-id="PageTitle"]')
        if page_title_span:
            return page_title_span.text().strip()

    @property
    def ville(self):
        return self.url_data.ville

    @property
    def quartier(self):
        return self.url_data.quartier

    @property
    def prix(self) -> int | None:
        price_span = self.tree.css_first("span#BuyPrice")
        price = int(re.sub(r"[^0-9]", "", price_span.text())) if price_span else None
        return price

    @property
    def revenus(self) -> int | None:
        revenus_text = self.carac_data.get("Revenus bruts potentiels")
        revenus_brut = int(re.sub(r"[^0-9]", "", revenus_text))
        return revenus_brut

    @property
    def description(self) -> str | None:
        description_div = self.tree.css_first('div[itemprop="description"]')
        description = description_div.text().strip() if description_div else None
        return description

    @property
    def addresse(self) -> str | None:
        address_h2 = self.tree.css_first('h2[itemprop="address"]')
        adresse = address_h2.text().strip() if address_h2 else None
        return adresse

    @property
    def annee_construction(self) -> int | None:
        annee_construction_text = self.carac_data.get("Année de construction")
        if annee_construction_text is not None:
            match = re.search(r"\b(18|19|20)\d{2}\b", annee_construction_text)
            if match:
                return int(match.group(0))
        return None

    @property
    def superficie_terrain(self) -> int | None:
        superficie_terrain_text = self.carac_data.get("Superficie du terrain")
        if superficie_terrain_text is not None:
            return int(re.sub(r"[^0-9]", "", superficie_terrain_text))

    @property
    def superficie_batiment(self) -> int | None:
        potential_values = ["Superficie du batiment", "Superficie du bâtiment (au sol)"]
        for value in potential_values:
            superficie_batiment_text = self.carac_data.get(value)
            if superficie_batiment_text is not None:
                return int(re.sub(r"[^0-9]", "", superficie_batiment_text))

    @property
    def superficie_habitable(self) -> int | None:
        superficie_habitable_text = self.carac_data.get("Superficie habitable")
        if superficie_habitable_text is not None:
            return int(re.sub(r"[^0-9]", "", superficie_habitable_text))

    @property
    def superficie_commerce(self) -> int | None:
        return self.carac_data.get("Superficie commerciale")

    @property
    def style_batiment(self) -> str | None:
        return self.carac_data.get("Style de bâtiment")

    @property
    def utilisation(self) -> str | None:
        potential_values = ["Utilisation", "Utilisation de la propriété"]
        for value in potential_values:
            if self.carac_data.get(value) is not None:
                return self.carac_data.get(value)

    @property
    def unites(self) -> list[str]:
        units_text = self.carac_data.get("Unité résidentielle")
        if units_text is None:
            units_text = self.carac_data.get("Unités résidentielles")
        if units_text is not None:
            unites = self._parse_unites(units_text)
            return unites
        return []

    @property
    def nombre_unites(self) -> int | None:
        # get nombre unites from extract_unites
        if self.unites is not None:
            return len(self.unites)
        else:
            nb_units_text = self.carac_data.get("Nombre d’unités")
            if nb_units_text is not None:
                match_unités = re.search(r"\((\d+)\)", nb_units_text)
                nombre_unites = int(match_unités.group(1)) if match_unités else None
                return nombre_unites
        return None

    @property
    def stationnement(self) -> int:
        try:
            # Retrieve 'Stationnement total' value
            stationnement_total = self.carac_data.get("Stationnement total")
            total_stationnement = (
                len(stationnement_total.split(",")) if stationnement_total else 0
            )

            # Retrieve 'Garage' text
            garage_text = self.carac_data.get("Garage")
            garage = 0
            if garage_text:
                match_garage = re.search(r"Garage \((\d+)\)", garage_text)
                garage = int(match_garage.group(1)) if match_garage else 0

            # Return the total number of stationnements
            return total_stationnement + garage

        except Exception as e:
            # Log the error and return a default value
            logger.error(f"Error calculating stationnement: {e}")
            return 0

    @property
    def total_taxes(self) -> int | None:
        # Locate the specific row in the taxes table
        taxes_total_row = self.tree.css_first(
            "div.financial-details-table-yearly tfoot tr.financial-details-table-total"
        )
        if taxes_total_row:
            taxes_total_value = taxes_total_row.css_first(
                "td.font-weight-bold.text-right"
            )
            if taxes_total_value:
                taxes_total_text = taxes_total_value.text().strip()
                return int(re.sub(r"[^0-9]", "", taxes_total_text))
        return None

    @property
    def eval_municipale(self) -> int | None:
        eval_row = self.tree.css_first("tr.financial-details-table-total")
        if eval_row:
            eval_municipal_value = eval_row.css_first("td.font-weight-bold.text-right")
            if eval_municipal_value:
                eval_municipale_text = eval_municipal_value.text().strip()
                return int(re.sub(r"[^0-9]", "", eval_municipale_text))
        return None

    @property
    def additional_characteristics(self) -> str | None:
        # Select all 'carac-title' elements
        misc_divs = self.tree.css(".carac-container")
        for container in misc_divs:
            title_div = container.css_first(".carac-title")
            if title_div and "Caractéristiques additionnelles" in title_div.text():
                # Extract the value if the title matches
                value_span = container.css_first(".carac-value span")
                if value_span:
                    return value_span.text().strip()
        return None

    def _get_carac_data(self):
        """Extract data stored as carac containers in the HTML."""
        carac_containers = self.tree.css(".carac-container")
        carac_data = {}
        for container in carac_containers:
            title_node = container.css_first(".carac-title")
            value_node = container.css_first(".carac-value span")

            if title_node and value_node:
                title = title_node.text().strip()
                value = value_node.text().strip()
                carac_data[title] = value
        return carac_data

    def _parse_unites(self, unites_str: str) -> list[str]:
        # Regular expression to match patterns like "1 x 3 ½" or "2 x 5 ½"
        pattern = r"(\d+)\s*x\s*(\d+)\s*½"

        unites = []
        matches = re.findall(pattern, unites_str)
        for count, value in matches:
            count = int(count)
            value = int(value)
            if 1 <= value <= 15:
                unites.extend([f"{value} 1/2"] * count)

        return unites


# TODO - Try scrapy for faster scraping?
class CentrisScraper:
    """Navigate all Centris listings for plexes and extract HTML"""

    def __init__(self, start_url: str = START_URL_PLEX):
        self.start_url = start_url

    def scrape_urls(self, num_pages: int = 5, headless: bool = True) -> list[str]:
        """
        Navigate through Centris thumbnail pages and collect URLs.

        Args:
            num_pages: Number of pages to scrape
            headless: Whether to run browser in headless mode

        Returns:
            List of fetched URLs
        """
        fetched_urls = []

        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(
                    headless=headless,
                    channel="chromium",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--no-sandbox",
                    ],
                )
                page = browser.new_page()
                page.set_viewport_size({"width": 1280, "height": 720})

                # Add user-agent to mimic a real browser
                page.set_extra_http_headers(
                    {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        )
                    }
                )

                page.goto(self.start_url)
                self.handle_cookies(page)
                self.sort_listings(page)

                for i in range(num_pages):
                    # Wait for initial load
                    page.wait_for_selector("div#property-result")
                    # Additional wait to ensure dynamic content is loaded
                    page.wait_for_selector("a.property-thumbnail-summary-link")
                    page.wait_for_timeout(2000)  # Extra safety wait

                    # Get all summary links directly
                    summary_links = page.query_selector_all(
                        "a.property-thumbnail-summary-link"
                    )
                    logger.info(
                        f"Found {len(summary_links)} properties on page {i + 1}"
                    )

                    for link in summary_links:
                        href = link.get_attribute("href")
                        if href and href.startswith("/fr/"):
                            full_url = f"https://www.centris.ca{href}"
                            fetched_urls.append(full_url)

                    # Load next batch of listings
                    try:
                        next_button = page.query_selector("li.next a")
                        if not next_button:
                            logger.info("No more listings to load.")
                            break

                        next_button.click()

                        # Wait for loading indicator or some element that indicates page transition
                        page.wait_for_selector("div#property-result")

                        # Additional wait for dynamic content
                        page.wait_for_selector("a.property-thumbnail-summary-link")
                        page.wait_for_timeout(1000)  # Extra safety wait

                    except Exception as e:
                        logger.error(f"Error navigating to next page: {e}")
                        break

            except Exception as e:
                logger.error(f"Critical error in navigation: {e}")
                fetched_urls = []

            finally:
                # Ensure browser closes even if an exception occurs
                if "browser" in locals():
                    browser.close()

        return fetched_urls

    def sort_listings(self, page):
        try:
            # Click the sort dropdown button and wait for menu
            sort_button = page.wait_for_selector("#selectSortById")
            sort_button.click()

            # Wait for dropdown menu to appear and select "Publication récente"
            page.wait_for_selector(".dropdown-menu.dropdown-menu-right.show")

            # Click the "Publication récente" option
            recent_option = page.wait_for_selector('a[data-option-value="3"]')
            recent_option.click()

            # Wait for the page to update with new sorting
            page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"Error sorting listings: {e}")

    def handle_cookies(self, page):
        try:
            accept_button = page.query_selector("button#didomi-notice-agree-button")
            if accept_button:
                logger.info(
                    "Cookie consent popup found. Clicking 'Accepter et continuer'."
                )
                accept_button.click()
                page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.info(f"No cookie consent popup found or error clicking: {e}")
