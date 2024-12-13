import requests
import re
from src.models import CentrisUrl
from selectolax.parser import HTMLParser
from collections import namedtuple

START_URL_PLEX = "https://www.centris.ca/fr/plex~a-vendre~montreal?view=Thumbnail"

ParsedUrl = namedtuple("ParsedUrl", ["url", "tree"])
UrlData = namedtuple("UrlData", ["centris_id", "ville", "quartier"])


class CentrisBienParser:
    """Extract relevant info data from a parsed HTML of a Centris Duplex listing  page."""

    def __init__(self, parsed_url: ParsedUrl) -> None:
        self.url = parsed_url.url
        self.tree = parsed_url.tree

    @property
    def carac_data(self):
        return self._get_carac_data()

    @property
    def url_data(self) -> UrlData:
        return self._extract_data_from_url()

    def _extract_data_from_url(self):
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

    def get_centris_id(self):
        return self.url_data.centris_id

    def extract_price(self) -> int | None:
        price_span = self.tree.css_first("span#BuyPrice")
        price = int(re.sub(r"[^0-9]", "", price_span.text())) if price_span else None
        return price

    def extract_revenus(self) -> int | None:
        revenus_text = self.carac_data.get("Revenus bruts potentiels")
        revenus_brut = int(re.sub(r"[^0-9]", "", revenus_text))
        return revenus_brut

    def extract_description(self) -> str | None:
        description_div = self.tree.css_first('div[itemprop="description"]')
        description = description_div.text().strip() if description_div else None
        return description

    def extract_address(self) -> str | None:
        address_h2 = self.tree.css_first('h2[itemprop="address"]')
        adresse = address_h2.text().strip() if address_h2 else None
        return adresse

    def extract_annee_construction(self) -> int | None:
        return self.carac_data.get("Année de construction")

    def extract_superficie_terrain(self) -> int | None:
        return self.carac_data.get("Superficie du terrain")

    def extract_superficie_batiment(self) -> int | None:
        return self.carac_data.get("Superficie du batiment")

    def extract_superficie_habitable(self) -> int | None:
        return self.carac_data.get("Superficie habitable")

    def extract_superficie_commerce(self) -> int | None:
        return self.carac_data.get("Superficie commerciale")

    def extract_style_batiment(self) -> str | None:
        return self.carac_data.get("Style de batiment")

    def extract_utilisation(self) -> str | None:
        return self.carac_data.get("Utilisation")

    def extract_nombre_unites(self) -> int | None:
        nb_units_text = self.carac_data.get("Nombre d'unites")
        match_unités = re.search(r"\((\d+)\)", nb_units_text)
        nombre_unites = int(match_unités.group(1)) if match_unités else None
        return nombre_unites

    def extract_unites(self) -> list[str]:
        units_text = self.carac_data.get("Unité résidentielle")
        if units_text is not None:
            unites = [unit.strip() for unit in units_text.split(",")]
            return unites
        return []

    def extract_stationnement(self) -> int:
        stationnement_total = self.carac_data.get("Stationnement total")
        # garage
        garage_text = self.carac_data.get("Garage")
        match_garage = re.search(r"Garage \((\d+)\)", garage_text)
        garage = int(match_garage.group(1)) if match_garage else 0
        return int(stationnement_total) + int(garage)

    def extract_total_taxes(self) -> int | None:
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

    def extract_eval_municipale(self) -> int | None:
        eval_row = self.tree.css_first("tr.financial-details-table-total")
        if eval_row:
            eval_municipal_value = eval_row.css_first("td.font-weight-bold.text-right")
            if eval_municipal_value:
                eval_municipale_text = eval_municipal_value.text().strip()
                return int(re.sub(r"[^0-9]", "", eval_municipale_text))
        return None

    def extract_additional_characteristics(self) -> str | None:
        additional_characteristics_row = self.tree.css_first(
            'div.carac-container:has(.carac-title:contains("Caractéristiques additionnelles"))'
        )
        if additional_characteristics_row:
            characteristics_value = additional_characteristics_row.css_first(
                ".carac-value span"
            )
            if characteristics_value:
                return characteristics_value.text().strip()
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

    def extract_data_from_url(self, url: CentrisUrl):
        """
        Extract town, neighborhood, and Centris listing ID from a Centris.ca URL.

        Args:
            url (str): A Centris.ca URL

        Returns:
            dict: A dictionary containing 'town', 'neighborhood', and 'centris_id'
        """
        # Validate URL
        try:
            # Extract location and ID from the path
            # The pattern is typically: /fr/property-type~transaction-type~town-neighborhood/listing-id
            match = re.search(r"/fr/[^/]+~[^/]+~([^/]+)/(\d+)", url.url)

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


class CentrisScraper:
    """Navigate all Centris listing for plexes and extract html"""

    def __init__(self):
        self.start_url = START_URL_PLEX

    def __call__(self, url) -> HTMLParser:
        html = self.get_html(url)
        tree = self.get_tree(html)
        return tree

    def get_html(self, url) -> str | None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch page {url}")

        return response.text

    def get_tree(self, html):
        return HTMLParser(html)

    def navigate_centris(self, num_pages: int = 100):
        i = 0
        while i < num_pages:
            # use playwright to navigate to the next page
            pass
        pass
