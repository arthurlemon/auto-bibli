import streamlit as st
import pandas as pd
from centris.db_models import PlexCentrisListingDB
from centris import Session


# TODO - Geocode address and place on a map


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
                "Prix/pi² terrain moyen": group["Prix/pi² terrain"].mean(),
                "Prix/pi² bâtiment moyen": group["Prix/pi² bâtiment"].mean(),
                "Ratio (Prix + 25ans taxes)/Revenus moyen": group[
                    "Ratio (Prix + 25ans taxes)/Revenus"
                ].mean(),
                "Diff Prix vs Éval (%) moyen": group["Diff Prix vs Éval (%)"].mean(),
            }
        )

    return pd.DataFrame(stats).sort_values("Nombre de propriétés", ascending=False)


def format_money(x):
    """Format numbers as currency with spaces"""
    if pd.isna(x):
        return None
    return f"{int(x):,}".replace(",", " ")


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived financial metrics"""
    # Create a copy to avoid modifying the original
    df = df.copy()

    # Price per square foot metrics
    if "Superficie terrain (pi²)" in df.columns:
        df["Prix/pi² terrain"] = df["Prix"] / df["Superficie terrain (pi²)"]
    if "Superficie bâtiment (pi²)" in df.columns:
        df["Prix/pi² bâtiment"] = df["Prix"] / df["Superficie bâtiment (pi²)"]
    if "Superficie habitable (pi²)" in df.columns:
        df["Prix/pi² habitable"] = df["Prix"] / df["Superficie habitable (pi²)"]

    # Calculate payback period considering taxes
    df["Ratio (Prix + 25ans taxes)/Revenus"] = (
        df["Prix"] + 25 * df["Taxes annuelles"]
    ) / df["Revenus annuels"]

    # Municipal evaluation metrics
    df["Diff Prix vs Éval (%)"] = (
        (df["Prix"] - df["Évaluation municipale"]) / df["Évaluation municipale"] * 100
    )

    return df


def load_listings_data() -> pd.DataFrame:
    """Load all listings from the database into a pandas DataFrame"""
    with Session.begin() as session:
        listings = session.query(PlexCentrisListingDB).all()

        data = [
            {
                "URL": listing.url,
                "Prix": listing.prix,
                "Titre": listing.title,
                "Adresse": listing.adresse,
                "Quartier": listing.quartier,
                "Superficie terrain (pi²)": listing.superficie_terrain,
                "Revenus annuels": listing.revenus,
                "Taxes annuelles": listing.taxes,
                "Évaluation municipale": listing.eval_municipale,
                "Année construction": listing.annee_construction,
                "Description": listing.description,
                "Unités": listing.unites,
                #'Nombre unités': listing.nombre_unites,
                "Superficie habitable (pi²)": listing.superficie_habitable,
                "Superficie bâtiment (pi²)": listing.superficie_batiment,
                "Superficie commerce (pi²)": listing.superficie_commerce,
                "Stationnement": listing.stationnement,
                "Utilisation": listing.utilisation,
                "Style bâtiment": listing.style_batiment,
                #'ID Centris': listing.centris_id,
                "Date de scrape": listing.date_scrape,
                "Ville": listing.ville,
            }
            for listing in listings
        ]

    df = pd.DataFrame(data)
    return calculate_metrics(df)


def main():
    st.set_page_config(
        page_title="Centris Plex Listings Dashboard", page_icon="🏢", layout="wide"
    )

    st.title("Centris Plex Listings Dashboard")

    # Load data
    df = load_listings_data()

    tab1, tab2 = st.tabs(["📊 Propriétés", "📈 Statistiques par quartier"])

    with tab1:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre de propriétés", format_money(len(df)))
        with col2:
            st.metric("Prix moyen", format_money(df["Prix"].mean()))
        with col3:
            st.metric("Prix médian", format_money(df["Prix"].median()))
        with col4:
            st.metric(
                "Propriétés avec revenus",
                format_money(df["Revenus annuels"].notna().sum()),
            )

        # Column configuration
        column_config = {
            "ID Centris": st.column_config.NumberColumn(
                "ID Centris",
                help="Identifiant unique Centris",
                format="%d",  # No thousand separator for IDs
            ),
            "URL": st.column_config.LinkColumn("URL", help="Lien vers l'annonce"),
            "Prix": st.column_config.NumberColumn(
                "Prix", help="Prix demandé", format="%f"
            ),
            "Date de scrape": st.column_config.DateColumn(
                "Date de scrape", help="Date du scrape"
            ),
            "Année construction": st.column_config.NumberColumn(
                "Année construction",
                help="Année de construction",
                format="%d",  # No thousand separator for years
            ),
            "Revenus annuels": st.column_config.NumberColumn(
                "Revenus annuels", help="Revenus annuels déclarés", format="%d"
            ),
            "Taxes annuelles": st.column_config.NumberColumn(
                "Taxes annuelles", help="Taxes annuelles", format="%d"
            ),
            "Évaluation municipale": st.column_config.NumberColumn(
                "Évaluation municipale", help="Évaluation municipale", format="%d"
            ),
            # New derived metrics
            "Prix/pi² terrain": st.column_config.NumberColumn(
                "Prix/pi² terrain", help="Prix par pied carré de terrain", format="%.2f"
            ),
            "Prix/pi² bâtiment": st.column_config.NumberColumn(
                "Prix/pi² bâtiment",
                help="Prix par pied carré de bâtiment",
                format="%.2f",
            ),
            "Prix/pi² habitable": st.column_config.NumberColumn(
                "Prix/pi² habitable",
                help="Prix par pied carré habitable",
                format="%.2f",
            ),
            "Ratio (Prix + 25ans taxes)/Revenus": st.column_config.NumberColumn(
                "Ratio (Prix + 25ans taxes)/Revenus",
                help="Années de revenus pour couvrir prix et 25 ans de taxes",
                format="%.1f",
            ),
            "Diff Prix vs Éval (%)": st.column_config.NumberColumn(
                "Diff Prix vs Éval (%)",
                help="Différence en % entre prix et évaluation municipale",
                format="%.1f%%",
            ),
        }

        # Filters
        st.subheader("Filtres")
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_cities = st.multiselect(
                "Villes", options=sorted(df["Ville"].dropna().unique())
            )
        with col2:
            selected_quartiers = st.multiselect(
                "Quartiers", options=sorted(df["Quartier"].dropna().unique())
            )
        with col3:
            price_range = st.slider(
                "Gamme de prix",
                min_value=int(df["Prix"].min()),
                max_value=int(df["Prix"].max()),
                value=(int(df["Prix"].min()), int(df["Prix"].max())),
                step=50000,
                format="%d",
            )

        # Apply filters
        filtered_df = df.copy()
        if selected_cities:
            filtered_df = filtered_df[filtered_df["Ville"].isin(selected_cities)]
        if selected_quartiers:
            filtered_df = filtered_df[filtered_df["Quartier"].isin(selected_quartiers)]
        filtered_df = filtered_df[
            (filtered_df["Prix"] >= price_range[0])
            & (filtered_df["Prix"] <= price_range[1])
        ]

        # Display the dataframe
        st.dataframe(
            filtered_df,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            height=600,
        )

    with tab2:
        st.subheader("Analyse par quartier")

        # Calculate statistics
        stats_df = calculate_quartier_stats(df)

        # Configure columns for the stats table
        stats_column_config = {
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
            "Prix/pi² bâtiment moyen": st.column_config.NumberColumn(
                "Prix/pi² bâtiment moyen",
                help="Prix moyen par pied carré de bâtiment",
                format="%.2f",
            ),
            "Ratio (Prix + 25ans taxes)/Revenus moyen": st.column_config.NumberColumn(
                "Ratio (Prix + 25ans taxes)/Revenus moyen",
                help="Nombre moyen d'années de revenus pour couvrir le prix",
                format="%.1f",
            ),
            "Diff Prix vs Éval (%) moyen": st.column_config.NumberColumn(
                "Diff Prix vs Éval (%) moyen",
                help="Différence moyenne en % entre prix et évaluation municipale",
                format="%.1f%%",
            ),
        }

        # Add metrics for overall statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Quartier le plus cher (prix médian)",
                stats_df.nlargest(1, "Prix médian")["Quartier"].iloc[0],
            )
        with col2:
            st.metric(
                "Meilleur Ratio (Prix + 25ans taxes)/Revenus",
                stats_df.nsmallest(1, "Ratio (Prix + 25ans taxes)/Revenus moyen")[
                    "Quartier"
                ].iloc[0],
            )
        with col3:
            st.metric(
                "Plus d'opportunités (vs éval. municipale)",
                stats_df.nsmallest(1, "Diff Prix vs Éval (%) moyen")["Quartier"].iloc[
                    0
                ],
            )

        # Display the statistics table
        st.dataframe(
            stats_df,
            column_config=stats_column_config,
            hide_index=True,
            use_container_width=True,
        )

        # Add a bar chart comparing median prices across quartiers
        st.subheader("Comparaison des prix médians par quartier")

        chart_data = stats_df[["Quartier", "Prix médian"]].sort_values(
            "Prix médian", ascending=True
        )
        st.bar_chart(chart_data.set_index("Quartier"), use_container_width=True)


if __name__ == "__main__":
    main()
