import streamlit as st
from centris.frontend.utils import (
    calculate_quartier_stats,
    load_listings_data,
    calculate_property_financial_metrics,
    order_df,
)
from centris.frontend.components import (
    display_property_metrics,
    display_property_filters,
    display_quartier_filters,
    set_column_config,
    geocode_addresses,
    create_map_data,
)


def main():
    st.set_page_config(
        page_title="Centris Plex Listings Dashboard", page_icon="🏢", layout="wide"
    )

    st.title("Centris Plex Listings Dashboard")
    display_map = st.checkbox("Afficher la carte des propriétés", value=False)
    # Load data
    raw_df = load_listings_data()
    if display_map:
        raw_df = geocode_addresses(raw_df.iloc[:2])
    df = calculate_property_financial_metrics(raw_df)
    df = order_df(df, include_latlong=display_map)

    tab1, tab2 = st.tabs(["📊 Propriétés", "📈 Statistiques par quartier"])

    with tab1:
        # Metrics
        display_property_metrics(df)

        # Column configuration
        column_config = set_column_config()

        # Filters
        st.subheader("Filtres")
        selected_quartiers, price_range = display_property_filters(df)

        # Apply filters
        filtered_df = df.copy()
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

        if display_map:
            st.subheader("Carte des propriétés")
            map_data = create_map_data(filtered_df)
            if not map_data.empty:
                st.map(map_data)

    with tab2:
        st.subheader("Analyse par quartier")

        stats_df = calculate_quartier_stats(df)
        stats_column_config = display_quartier_filters()

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
