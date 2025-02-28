import streamlit as st
from centris.frontend.utils import format_money, clean_address
import pandas as pd
from geopy.geocoders import Nominatim
import time


def geocode_addresses(df):
    geolocator = Nominatim(user_agent="centris_app", timeout=5)

    if "latitude" not in df.columns:
        df["latitude"] = None
        df["longitude"] = None

    mask = df[["latitude", "longitude"]].isna().any(axis=1)
    for idx, row in df[mask].iterrows():
        clean_addr = clean_address(row["Adresse"])
        address = f"{clean_addr}, {row['Ville']}, Québec, Canada"
        try:
            # TODO - Save the geocoding results to the DB to avoid re-geocoding
            location = geolocator.geocode(address)
            if location:
                df.at[idx, "latitude"] = location.latitude
                df.at[idx, "longitude"] = location.longitude
            time.sleep(1)  # Respect rate limits
        except Exception as e:
            print(f"Error geocoding {address}: {str(e)}")
            continue

    return df


def create_map_data(df):
    # Only keep rows with valid coordinates
    map_df = df[df["latitude"].notna() & df["longitude"].notna()].copy()

    # Format price for tooltip
    map_df["Prix"] = map_df["Prix"].apply(lambda x: f"{x:,.0f}$")

    return map_df[["latitude", "longitude", "Prix", "Adresse"]]


def display_property_metrics(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nombre de propriétés", format_money(len(df)))
    with col2:
        st.metric("Prix médian", format_money(df["Prix"].median()))
    with col3:
        st.metric(
            "Revenus médians",
            format_money(df["Revenus annuels"].median()),
        )
    with col4:
        st.metric(
            "Taxes médianes",
            format_money(df["Taxes annuelles"].median()),
        )


def display_property_filters(df: pd.DataFrame) -> tuple[list[str], tuple[int, int]]:
    col1, col2 = st.columns(2)
    with col1:
        selected_quartiers = st.multiselect(
            "Quartiers", options=sorted(df["Quartier"].dropna().unique())
        )
    with col2:
        price_range = st.slider(
            "Gamme de prix",
            min_value=int(df["Prix"].min()),
            max_value=int(df["Prix"].max()),
            value=(int(df["Prix"].min()), int(df["Prix"].max())),
            step=50000,
            format="%d",
        )

    return selected_quartiers, price_range


def display_quartier_filters():
    return {
        "Quartier": st.column_config.TextColumn("Quartier", help="Nom du quartier"),
        "Nombre de propriétés": st.column_config.NumberColumn(
            "Nombre de propriétés",
            help="Nombre total de propriétés dans le quartier",
            format="%d",
        ),
        "Prix moyen": st.column_config.NumberColumn(
            "Prix moyen", help="Prix moyen des propriétés", format="%d"
        ),
        "Prix médian": st.column_config.NumberColumn(
            "Prix médian", help="Prix médian des propriétés", format="%d"
        ),
        "Prix min": st.column_config.NumberColumn(
            "Prix minimum", help="Prix le plus bas", format="%d"
        ),
        "Prix max": st.column_config.NumberColumn(
            "Prix maximum", help="Prix le plus élevé", format="%d"
        ),
        "Prix/pi² terrain moyen": st.column_config.NumberColumn(
            "Prix/pi² terrain moyen",
            help="Prix moyen par pied carré de terrain",
            format="%.2f",
        ),
        "Annees Payback moyen": st.column_config.NumberColumn(
            "Annees Payback moyen",
            help="Nombre moyen d'années de revenus pour couvrir le prix",
            format="%.1f",
        ),
        "Diff Prix vs Éval (%) moyen": st.column_config.NumberColumn(
            "Diff Prix vs Éval (%) moyen",
            help="Différence moyenne en % entre prix et évaluation municipale",
            format="%.1f%%",
        ),
    }


def set_column_config():
    return {
        "URL": st.column_config.LinkColumn(
            "URL",
            display_text="https://www\.centris\.ca/fr/(.*?)/(.*?)?view=Summary",
            help="Lien vers l'annonce",
        ),
        "Prix": st.column_config.NumberColumn("Prix", help="Prix demandé", format="%f"),
        "Année construction": st.column_config.NumberColumn(
            "Année construction",
            help="Année de construction",
            format="%d",  # No thousand separator for years
        ),
        "Revenus annuels": st.column_config.NumberColumn(
            "Revenus annuels", help="Revenus annuels", format="%d"
        ),
        "Taxes annuelles": st.column_config.NumberColumn(
            "Taxes annuelles", help="Taxes annuelles", format="%d"
        ),
        "Évaluation municipale": st.column_config.NumberColumn(
            "Évaluation municipale", help="Évaluation municipale", format="%d"
        ),
        # New derived metrics
        "Prix/pi² terrain": st.column_config.NumberColumn(
            "Prix/pi² terrain", help="Prix par pied carré de terrain", format="%d"
        ),
        "Annees Payback": st.column_config.NumberColumn(
            "Annees Payback",
            help="Années de revenus pour couvrir prix et 25 ans de taxes",
            format="%d",
        ),
        "Diff Prix vs Éval (%)": st.column_config.NumberColumn(
            "Diff Prix vs Éval (%)",
            help="Différence en % entre prix et évaluation municipale",
            format="%.1f%%",
        ),
    }
