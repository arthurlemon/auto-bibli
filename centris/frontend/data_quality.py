import pandas as pd
from ydata_profiling import ProfileReport
import streamlit as st
from centris.backend.db_models import PlexCentrisListingDB
from centris import Session


def load_data() -> pd.DataFrame:
    """Load data from database into DataFrame"""
    with Session.begin() as session:
        listings = session.query(PlexCentrisListingDB).all()

        data = [
            {
                "ID Centris": listing.centris_id,
                "Prix": listing.prix,
                "Date scrape": listing.date_scrape,
                "Titre": listing.title,
                "Année construction": listing.annee_construction,
                "Description": listing.description,
                "Unités": listing.unites,
                "Nombre unités": listing.nombre_unites,
                "Superficie habitable": listing.superficie_habitable,
                "Superficie bâtiment": listing.superficie_batiment,
                "Superficie commerce": listing.superficie_commerce,
                "Superficie terrain": listing.superficie_terrain,
                "Stationnement": listing.stationnement,
                "Utilisation": listing.utilisation,
                "Style bâtiment": listing.style_batiment,
                "Adresse": listing.adresse,
                "Ville": listing.ville,
                "Quartier": listing.quartier,
                "Revenus annuels": listing.revenus,
                "Taxes annuelles": listing.taxes,
                "Évaluation municipale": listing.eval_municipale,
            }
            for listing in listings
        ]

    return pd.DataFrame(data)


def compute_basic_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute basic data quality metrics"""
    metrics = []
    total_rows = len(df)

    for column in df.columns:
        missing = df[column].isna().sum()
        zeros = (
            (df[column] == 0).sum() if pd.api.types.is_numeric_dtype(df[column]) else 0
        )
        unique_values = df[column].nunique()

        metrics.append(
            {
                "Colonne": column,
                "Type": str(df[column].dtype),
                "Valeurs manquantes (%)": (missing / total_rows) * 100,
                "Valeurs zéro (%)": (zeros / total_rows) * 100,
                "Valeurs uniques": unique_values,
                "Échantillon valeurs": str(
                    df[column]
                    .dropna()
                    .sample(min(3, len(df[column].dropna())))
                    .tolist()
                ),
            }
        )

    return pd.DataFrame(metrics)


def main():
    st.set_page_config(
        page_title="Centris Data Quality Analysis", page_icon="📊", layout="wide"
    )

    st.title("Analyse de la qualité des données Centris")

    # Load data
    df = load_data()

    # Display basic dataset info
    st.subheader("Aperçu général")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre total de propriétés", len(df))
    with col2:
        st.metric("Nombre de colonnes", len(df.columns))
    with col3:
        st.metric(
            "Période de collecte",
            f"{df['Date scrape'].min()} à {df['Date scrape'].max()}",
        )

    # Basic metrics table
    st.subheader("Métriques par colonne")
    metrics_df = compute_basic_metrics(df)

    # Configure columns for the metrics table
    metrics_column_config = {
        "Colonne": st.column_config.TextColumn("Colonne", help="Nom de la colonne"),
        "Type": st.column_config.TextColumn("Type", help="Type de données"),
        "Valeurs manquantes (%)": st.column_config.NumberColumn(
            "Valeurs manquantes (%)",
            help="Pourcentage de valeurs manquantes",
            format="%.1f%%",
        ),
        "Valeurs zéro (%)": st.column_config.NumberColumn(
            "Valeurs zéro (%)",
            help="Pourcentage de valeurs égales à zéro",
            format="%.1f%%",
        ),
        "Valeurs uniques": st.column_config.NumberColumn(
            "Valeurs uniques", help="Nombre de valeurs uniques", format="%d"
        ),
        "Échantillon valeurs": st.column_config.TextColumn(
            "Échantillon valeurs", help="Exemple de valeurs"
        ),
    }

    st.dataframe(
        metrics_df.sort_values("Valeurs manquantes (%)", ascending=False),
        column_config=metrics_column_config,
        hide_index=True,
        use_container_width=True,
    )

    # Generate detailed profile report
    st.subheader("Rapport détaillé")
    if st.button("Générer un rapport détaillé (peut prendre quelques minutes)"):
        with st.spinner("Génération du rapport en cours..."):
            profile = ProfileReport(
                df, title="Rapport qualité des données Centris", minimal=True
            )
            # Save and display the report
            profile.to_file("artifacts/centris_data_quality_report.html")
            st.success("Rapport généré avec succès!")
            with open(
                "artifacts/centris_data_quality_report.html", "r", encoding="utf-8"
            ) as f:
                st.components.v1.html(f.read(), height=1000, scrolling=True)


if __name__ == "__main__":
    main()
