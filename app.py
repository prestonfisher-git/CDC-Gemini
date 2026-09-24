import streamlit as st
from src.data_loader import load_data
from src.components import render_header, render_sidebar, render_kpi_cards
from src.visualizations import (
    chart_monthly_trend,
    chart_sex_comparison,
    chart_state_ranking,
    chart_choropleth_map,
    chart_state_month_heatmap,
    chart_top_bottom_comparison
)

# Page Configuration
st.set_page_config(
    page_title="CDC Provisional Natality Dashboard",
    page_icon="👶",
    layout="wide"
)

# Main Application Entry Point
def main():
    render_header()
    
    # Ingest Data
    raw_df = load_data()

    # Sidebar Filter Controls
    filtered_df, selected_states, selected_months, selected_sex = render_sidebar(raw_df)

    # Empty State Handling
    if filtered_df.empty:
        st.warning("⚠️ No observations match the selected filter combination. Please broaden your selection criteria.")
        return

    # Metric Cards
    render_kpi_cards(filtered_df, selected_states, selected_months)

    # Dashboard Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "🗺️ Geographic Analysis", 
        "👫 Monthly & Sex Analysis", 
        "📋 Data Table & Download", 
        "ℹ️ About the Data"
    ])

    with tab1:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.plotly_chart(chart_monthly_trend(filtered_df), use_container_width=True)
        with col_b:
            top_bottom_fig = chart_top_bottom_comparison(filtered_df)
            if top_bottom_fig:
                st.plotly_chart(top_bottom_fig, use_container_width=True)
            else:
                st.info("Select at least 2 geographies to view top/bottom comparison.")

    with tab2:
        st.plotly_chart(chart_choropleth_map(filtered_df), use_container_width=True)
        st.divider()
        st.plotly_chart(chart_state_ranking(filtered_df), use_container_width=True)

    with tab3:
        col_c, col_d = st.columns(2)
        with col_c:
            st.plotly_chart(chart_sex_comparison(filtered_df), use_container_width=True)
        with col_d:
            st.plotly_chart(chart_state_month_heatmap(filtered_df), use_container_width=True)

    with tab4:
        st.subheader("Filtered Natality Dataset")
        st.markdown("Search, sort, or export the currently active filtered observations below.")
        
        display_cols = ['state_of_residence', 'month', 'sex_of_infant', 'births', 'state_abbr']
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
        
        csv_data = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="filtered_cdc_natality_2025.csv",
            mime="text/csv"
        )

    with tab5:
        st.markdown("""
        ### About the Dataset & Business Analytics Guide
        
        #### Key Concepts: Counts vs. Rates
        * **Birth Count**: The aggregate number of live births occurring within a specific geography and timeframe.
        * **Birth Rate**: The number of live births per unit of population (typically per 1,000 residents). 
        * **Analytics Note**: Absolute birth counts reflect healthcare demand and resource allocation needs. However, higher counts in populous states (e.g., California, Texas) do not imply higher fertility rates without controlling for base population size.

        #### Data Provenance & Limitations
        * **Source**: CDC National Center for Health Statistics (NCHS) Provisional Natality Statistics.
        * **Status**: Figures are provisional and subject to standard administrative adjustments prior to final release.
        """)

if __name__ == "__main__":
    main()
