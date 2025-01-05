import pandas as pd
from centris.backend.db_models import PlexCentrisListingDB
from centris import Session


def calculate_quartier_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate price statistics per quartier"""
    stats = []

    for quartier, group in df.groupby("Quartier"):
        if pd.isna(quartier):
            continue

        stats.append(
            {
                "Quartier": quartier,
                "Nombre de propriétés": len(group),
                "Prix moyen": group["Prix"].mean(),
                "Prix médian": group["Prix"].median(),
                "Prix min": group["Prix"].min(),
                "Prix max": group["Prix"].max(),
                "Prix/pi² terrain médian": group["Prix/pi² terrain"].median(),
                "Annees Payback médian": group["Annees Payback"].median(),
                "Diff Prix vs Éval (%) médian": group["Diff Prix vs Éval (%)"].median(),
            }
        )

    return pd.DataFrame(stats).sort_values("Quartier")


def format_money(x):
    """Format numbers as currency with spaces"""
    if pd.isna(x):
        return None
    return f"{int(x):,}".replace(",", " ")


def calculate_property_financial_metrics(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived financial metrics"""
    # Create a copy to avoid modifying the original
    enriched_df = raw_df.copy()

    # Price per square foot metrics
    if "Superficie terrain (pi²)" in enriched_df.columns:
        enriched_df["Prix/pi² terrain"] = (
            enriched_df["Prix"] / enriched_df["Superficie terrain (pi²)"]
        )

    # not computing because too many missing values (>=80%)
    # if "Superficie bâtiment (pi²)" in df.columns:
    #     df["Prix/pi² bâtiment"] = df["Prix"] / df["Superficie bâtiment (pi²)"]
    # if "Superficie habitable (pi²)" in df.columns:
    #     df["Prix/pi² habitable"] = df["Prix"] / df["Superficie habitable (pi²)"]

    # Calculate payback period considering taxes
    enriched_df["Annees Payback"] = enriched_df["Prix"] / (
        enriched_df["Revenus annuels"] - enriched_df["Taxes annuelles"]
    )

    enriched_df["Ratio Revenus / Prix"] = (
        enriched_df["Revenus annuels"] / enriched_df["Prix"]
    ) * 100

    # Municipal evaluation metrics
    enriched_df["Diff Prix vs Éval (%)"] = (
        (enriched_df["Prix"] - enriched_df["Évaluation municipale"])
        / enriched_df["Évaluation municipale"]
        * 100
    )

    return enriched_df


def order_df(df, include_latlong=False):
    display_columns = [
        "Quartier",
        "URL",
        "Prix",
        "Évaluation municipale",
        "Superficie terrain (pi²)",
        "Prix/pi² terrain",
        "Diff Prix vs Éval (%)",
        "Revenus annuels",
        "Taxes annuelles",
        "Annees Payback",
        "Ratio Revenus / Prix",
        "Adresse",
        "Année construction",
        "Description",
        "Unités",
        "Stationnement",
        "Utilisation",
        "Date de scrape",
    ]

    if include_latlong:
        display_columns.append("latitude")
        display_columns.append("longitude")
    df = df.sort_values("Date de scrape", ascending=False)
    return df[display_columns]


def clean_address(address):
    main_part = "".join(address.split(",")[:2])
    return main_part


def load_listings_data() -> pd.DataFrame:
    """Load all listings from the database into a pandas DataFrame"""
    with Session.begin() as session:
        listings = session.query(PlexCentrisListingDB).all()

        data = [
            {
                "Quartier": listing.quartier,
                "URL": listing.url,
                "Prix": listing.prix,
                "Titre": listing.title,
                "Adresse": listing.adresse,
                "Superficie terrain (pi²)": listing.superficie_terrain,
                "Revenus annuels": listing.revenus,
                "Taxes annuelles": listing.taxes,
                "Évaluation municipale": listing.eval_municipale,
                "Année construction": listing.annee_construction,
                "Description": listing.description,
                "Unités": listing.unites,
                #'Nombre unités': listing.nombre_unites,
                # "Superficie habitable (pi²)": listing.superficie_habitable,
                # "Superficie bâtiment (pi²)": listing.superficie_batiment,
                # "Superficie commerce (pi²)": listing.superficie_commerce,
                "Stationnement": listing.stationnement,
                "Utilisation": listing.utilisation,
                # "Style bâtiment": listing.style_batiment,
                "ID Centris": listing.centris_id,
                "Date de scrape": listing.date_scrape,
                "Ville": listing.ville,
            }
            for listing in listings
        ]

    return pd.DataFrame(data)
