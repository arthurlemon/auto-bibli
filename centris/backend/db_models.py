from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from centris.backend.utils import get_default_date
from typing import Optional


class Base(DeclarativeBase):
    pass


# TODO - Add "active" field to track if listing is still active
# Propably requires calling the URL and checking if there is a redirect to the summary page
# Annoying: publication_date cannot be scraped from the HTML
class PlexCentrisListingDB(Base):
    __tablename__ = "plex_centris_listings"

    # required fields
    centris_id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    prix: Mapped[int]
    date_scrape: Mapped[str] = mapped_column(default=get_default_date)

    # optional fields
    title: Mapped[Optional[str]]
    annee_construction: Mapped[Optional[int]]
    description: Mapped[Optional[str]]
    unites: Mapped[Optional[str]]
    nombre_unites: Mapped[Optional[int]]
    superficie_habitable: Mapped[Optional[int]]
    superficie_batiment: Mapped[Optional[int]]
    superficie_commerce: Mapped[Optional[int]]
    superficie_terrain: Mapped[Optional[int]]
    stationnement: Mapped[Optional[int]]
    utilisation: Mapped[Optional[str]]
    style_batiment: Mapped[Optional[str]]
    adresse: Mapped[Optional[str]]
    ville: Mapped[Optional[str]]
    quartier: Mapped[Optional[str]]
    revenus: Mapped[Optional[int]]
    taxes: Mapped[Optional[int]]
    eval_municipale: Mapped[Optional[int]]
