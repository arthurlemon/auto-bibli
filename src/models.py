import re
from pydantic import BaseModel, field_validator
from enum import Enum
from urllib.parse import urlparse


class Utilisation(str, Enum):
    Résidentiel = "Résidentiel"
    Commercial = "Commercial"


class CentrisUrl(BaseModel):
    url: str

    @field_validator("url")
    def validate_centrics_url(cls, value):
        parsed_url = urlparse(value)

        if parsed_url.scheme != "https" or parsed_url.netloc != "www.centris.ca":
            raise ValueError("URL must belong to 'https://www.centris.ca'.")
        if not parsed_url.path.startswith("/fr/"):
            raise ValueError("French version of the website must be used.")

        path_parts = parsed_url.path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Path must include dynamic segments '<x>~<y>' and '<id>'.")

        # Validate the query parameters
        query_params = dict(
            param.split("=") for param in parsed_url.query.split("&") if "=" in param
        )
        if query_params.get("view") != "Summary":
            raise ValueError("Query parameter 'view' must be set to 'Summary'.")

        return value


class CustomDateFormat(BaseModel):
    date: str

    @field_validator("date")
    def validate_date(cls, value):
        # format must be "YYYY-MM-DD"
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError("Date must be in the format 'YYYY-MM-DD'.")
        return value


class BienCentrisDuplex(BaseModel):
    centris_id: int
    url: CentrisUrl
    adresse: str
    ville: str
    quartier: str
    annee_construction: int
    utilisation: Utilisation | list[Utilisation] | None = None
    superficie_habitable: int | None = None  # pc
    superficie_batiment: int | None = None  # pc
    superficie_commerce: int | None = None  # pc
    superficie_terrain: int | None = None  # pc
    garage: int = 0
    prix: int
    eval_municipale: int
    taxes: int
    frais: int = 0
    revenus: int | None = None
    description: str | None = None
    date_scrape: CustomDateFormat
