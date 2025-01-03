import json
from centris.backend.db_models import PlexCentrisListingDB


def map_bien_centris_to_orm(
    pydantic_model: PlexCentrisListingDB,
) -> PlexCentrisListingDB:
    """
    Maps an instance of BienCentrisDuplex (Pydantic model) to PlexCentrisListings (SQLAlchemy ORM model).
    """
    return PlexCentrisListingDB(
        centris_id=pydantic_model.centris_id,
        url=pydantic_model.url,
        title=pydantic_model.title,
        annee_construction=pydantic_model.annee_construction,
        description=pydantic_model.description,
        unites=json.dumps(pydantic_model.unites)
        if pydantic_model.unites
        else None,  # Serialize list to JSON
        nombre_unites=pydantic_model.nombre_unites,
        superficie_habitable=pydantic_model.superficie_habitable,
        superficie_batiment=pydantic_model.superficie_batiment,
        superficie_commerce=pydantic_model.superficie_commerce,
        superficie_terrain=pydantic_model.superficie_terrain,
        stationnement=pydantic_model.stationnement,
        utilisation=pydantic_model.utilisation,
        style_batiment=pydantic_model.style_batiment,
        adresse=pydantic_model.adresse,
        ville=pydantic_model.ville,
        quartier=pydantic_model.quartier,
        prix=pydantic_model.prix,
        revenus=pydantic_model.revenus,
        taxes=pydantic_model.taxes,
        eval_municipale=pydantic_model.eval_municipale,
        date_scrape=pydantic_model.date_scrape,
    )
