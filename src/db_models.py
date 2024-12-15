from sqlmodel import Field, SQLModel, create_engine
from datetime import datetime


class BienCentrisDuplex(SQLModel, table=True):
    url: str = Field(primary_key=True)
    centris_id: int
    title: str
    annee_construction: int
    description: str | None = None
    unites: str | None = None
    nombre_unites: int | None = None
    superficie_habitable: int | None = None  # pc
    superficie_batiment: int | None = None  # pc
    superficie_commerce: int | None = None  # pc
    superficie_terrain: int | None = None  # pc
    stationnement: int | None = None
    utilisation: str | None = None
    style_batiment: str | None = None
    adresse: str
    ville: str
    quartier: str
    prix: int
    revenus: int | None = None
    taxes: int | None = None
    eval_municipale: int | None = None
    date_scrape: datetime


sqlite_file_name = "../db/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
