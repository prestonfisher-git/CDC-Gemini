import streamlit as st
import pandas as pd
from src.utils import MONTH_ORDER

def render_header():
    """Renders dashboard header, source attribution, and required notices."""
    st.title("Provisional US Natality Data Explorer (2025)")
    st.markdown(
        "Interactive dashboard designed for exploring geographic, seasonal, and demographic pattern variations in birth volumes."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.warning(
            "⚠️ **Provisional Data Notice**: These figures are preliminary and subject to revision."
        )
    with col2:
        st.info(
            "📊 **Metric Notice**: Figures denote absolute **Birth Counts**, NOT birth rates (population denominators are excluded)."
        )
    
    st.caption("Data Source: CDC National Center for Health Statistics (NCHS) Provisional Natality Database")
    st.divider()

def render_sidebar(df: pd.DataFrame):
    """Renders stateful sidebar filters and returns filtered dataframe."""
    st.sidebar.header("Filter Controls")

    all_states = sorted(df['state_of_residence'].dropna().unique().tolist())
    all_months = [m for m in MONTH_ORDER if m in df['month'].unique()]
    all_sexes = ['All', 'Female', 'Male']

    # Initialize default session state
    if 'selected_states' not in st.session_state:
        st.session_state.selected_states = all_states
    if 'selected_months' not in st.session_state:
        st.session_state.selected_months = all_months
    if 'selected_sex' not in st.session_state:
        st.session_state.selected_sex = 'All'

    # Reset & Select All buttons
    col_btn1, col_btn2 = st.sidebar.columns(2)
    if col_btn1.button("Select All", use_container_width=True):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sex = 'All'
        st.rerun()

    if col_btn2.button("Reset Filters", use_container_width=True):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sex = 'All'
        st.rerun()

    # Selection controls
    selected_states = st.sidebar.multiselect(
        "Select State(s) / Geography:",
        options=all_states,
        default=st.session_state.selected_states,
        key='ms_states'
    )
    
    selected_months = st.sidebar.multiselect(
        "Select Month(s):",
        options=all_months,
        default=st.session_state.selected_months,
        key='ms_months'
    )

    selected_sex = st.sidebar.radio(
        "Select Infant Sex:",
        options=all_sexes,
        index=all_sexes.index(st.session_state.selected_sex),
        key='rd_sex'
    )

    # Active filter summary box
    st.sidebar.markdown("---")
    st.sidebar.subheader("Active Filter Summary")
    st.sidebar.write(f"• **States Selected**: {len(selected_states)} / {len(all_states)}")
    st.sidebar.write(f"• **Months Selected**: {len(selected_months)} / {len(all_months)}")
    st.sidebar.write(f"• **Sex Selected**: {selected_sex}")

    # Apply filters
    filtered_df = df[
        (df['state_of_residence'].isin(selected_states)) &
        (df['month'].isin(selected_months))
    ]

    if selected_sex != 'All':
        filtered_df = filtered_df[filtered_df['sex_of_infant'] == selected_sex]

    return filtered_df, selected_states, selected_months, selected_sex

def render_kpi_cards(filtered_df: pd.DataFrame, selected_states: list, selected_months: list):
    """Displays KPI metrics."""
    total_births = filtered_df['births'].sum()
    num_states = len(selected_states)
    
    # Calculate monthly average across selected months
    avg_births_per_month = total_births / len(selected_months) if selected_months else 0

    # Highest geography calculation
    geo_grouped = filtered_df.groupby('state_of_residence', observed=True)['births'].sum()
    top_geo = geo_grouped.idxmax() if not geo_grouped.empty and total_births > 0 else "N/A"
    top_geo_val = geo_grouped.max() if not geo_grouped.empty and total_births > 0 else 0

    # Highest month calculation
    month_grouped = filtered_df.groupby('month', observed=True)['births'].sum()
    top_month = month_grouped.idxmax() if not month_grouped.empty and total_births > 0 else "N/A"
    top_month_val = month_grouped.max() if not month_grouped.empty and total_births > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Selected Births", f"{total_births:,}")
    col2.metric("Selected Geographies", f"{num_states}")
    col3.metric("Avg Births / Month", f"{int(round(avg_births_per_month)):,}")
    col4.metric("Top Geography", f"{top_geo}", f"{top_geo_val:,} births" if top_geo != "N/A" else None)
    col5.metric("Peak Month", f"{top_month}", f"{top_month_val:,} births" if top_month != "N/A" else None)
    st.divider()
