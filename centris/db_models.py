from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from centris.utils import get_default_date
from typing import Optional


class Base(DeclarativeBase):
    pass


class PlexCentrisListingDB(Base):
    __tablename__ = "plex_centris_listings"

    centris_id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
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
    prix: Mapped[int]
    revenus: Mapped[Optional[int]]
    taxes: Mapped[Optional[int]]
    eval_municipale: Mapped[Optional[int]]
    date_scrape: Mapped[str] = mapped_column(default=get_default_date)
