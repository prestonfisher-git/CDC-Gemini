import os
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURATION & UTILITIES
# ==============================================================================

# Standard state name to two-letter abbreviation mapping
STATE_TO_ABBR = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
    'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
    'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June', 
    'July', 'August', 'September', 'October', 'November', 'December'
]

def format_number(val: float) -> str:
    """Format numbers with thousands separators."""
    if val is None or pd.isna(val):
        return "N/A"
    return f"{int(round(val)):,}"

# ==============================================================================
# DATA LOADING & CACHING
# ==============================================================================

@st.cache_data
def load_data(file_name: str = "Provisional_Natality_2025_CDC1.csv") -> pd.DataFrame:
    """
    Loads natality dataset, validates required columns, and transforms types.
    Searches both current directory and a 'data/' subfolder for cloud compatibility.
    """
    path = Path(file_name)
    if not path.exists():
        path = Path("data") / file_name
        if not path.exists():
            st.error(f"Data file '{file_name}' not found. Please place the CSV file in the root directory or data/ folder.")
            st.stop()

    df = pd.read_csv(path)

    # Required columns validation check
    required_cols = {'state_of_residence', 'month', 'month_code', 'year_code', 'sex_of_infant', 'births'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        st.error(f"Data validation failed. Missing required columns: {missing}")
        st.stop()

    # Data transformation
    df['state_abbr'] = df['state_of_residence'].map(STATE_TO_ABBR)
    df['month'] = pd.Categorical(df['month'], categories=MONTH_ORDER, ordered=True)
    df['births'] = pd.to_numeric(df['births'], errors='coerce').fillna(0).astype(int)

    return df

# ==============================================================================
# HEADER & SIDEBAR COMPONENTS
# ==============================================================================

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

    # Action Buttons: Select All & Reset
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
    
    # Monthly average across selected months
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

# ==============================================================================
# CHARTS & VISUALIZATIONS
# ==============================================================================

def chart_monthly_trend(df: pd.DataFrame):
    """Monthly birth volume line chart."""
    trend_df = df.groupby('month', observed=True)['births'].sum().reset_index()
    
    fig = px.line(
        trend_df, x='month', y='births',
        markers=True,
        title="Total Monthly Birth Trend",
        labels={'month': 'Month', 'births': 'Birth Count'},
        template="plotly_white"
    )
    fig.update_traces(line_color='#1E3A8A', line_width=3, marker_size=8)
    fig.update_yaxes(rangemode="tozero")
    return fig

def chart_sex_comparison(df: pd.DataFrame):
    """Female vs Male births grouped bar chart."""
    sex_df = df.groupby(['month', 'sex_of_infant'], observed=True)['births'].sum().reset_index()
    
    fig = px.bar(
        sex_df, x='month', y='births', color='sex_of_infant',
        barmode='group',
        title="Birth Comparison by Infant Sex and Month",
        labels={'month': 'Month', 'births': 'Birth Count', 'sex_of_infant': 'Infant Sex'},
        color_discrete_map={'Female': '#2563EB', 'Male': '#D97706'},
        template="plotly_white"
    )
    fig.update_yaxes(rangemode="tozero")
    return fig

def chart_state_ranking(df: pd.DataFrame):
    """Horizontal bar chart for state rankings."""
    rank_df = df.groupby('state_of_residence', observed=True)['births'].sum().reset_index()
    rank_df = rank_df.sort_values(by='births', ascending=True)

    fig = px.bar(
        rank_df, x='births', y='state_of_residence',
        orientation='h',
        title="Total Births by Geography",
        labels={'state_of_residence': 'State / Geography', 'births': 'Birth Count'},
        color='births',
        color_continuous_scale='Blues',
        template="plotly_white"
    )
    fig.update_layout(height=max(400, len(rank_df) * 20), showlegend=False)
    fig.update_xaxes(rangemode="tozero")
    return fig

def chart_choropleth_map(df: pd.DataFrame):
    """Choropleth map of US states."""
    map_df = df.groupby(['state_abbr', 'state_of_residence'], observed=True)['births'].sum().reset_index()

    fig = px.choropleth(
        map_df,
        locations='state_abbr',
        locationmode="USA-states",
        color='births',
        scope="usa",
        hover_name='state_of_residence',
        hover_data={'births': ':,', 'state_abbr': False},
        title="Geographic Distribution of Selected Births",
        color_continuous_scale="Cividis"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

def chart_state_month_heatmap(df: pd.DataFrame):
    """Heatmap showing state-by-month distribution."""
    pivot_df = df.pivot_table(
        index='state_of_residence', columns='month', values='births', aggfunc='sum', observed=False
    ).fillna(0)

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="State / Geography", color="Birth Count"),
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        color_continuous_scale="Viridis",
        aspect="auto",
        title="State-by-Month Birth Distribution Heatmap"
    )
    fig.update_layout(height=max(400, len(pivot_df) * 18))
    return fig

def chart_top_bottom_comparison(df: pd.DataFrame):
    """Top 5 vs Bottom 5 geographies comparison."""
    geo_df = df.groupby('state_of_residence', observed=True)['births'].sum().reset_index()
    if len(geo_df) < 2:
        return None

    geo_sorted = geo_df.sort_values(by='births', ascending=False)
    top_5 = geo_sorted.head(5).copy()
    top_5['Group'] = 'Top 5 Geographies'
    
    bottom_5 = geo_sorted.tail(5).copy()
    bottom_5['Group'] = 'Bottom 5 Geographies'

    combined = pd.concat([top_5, bottom_5])

    fig = px.bar(
        combined, x='state_of_residence', y='births', color='Group',
        title="Volume Comparison: Top 5 vs Bottom 5 Geographies",
        labels={'state_of_residence': 'Geography', 'births': 'Birth Count'},
        color_discrete_map={'Top 5 Geographies': '#1E40AF', 'Bottom 5 Geographies': '#93C5FD'},
        template="plotly_white"
    )
    fig.update_yaxes(rangemode="tozero")
    return fig

# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

def main():
    st.set_page_config(
        page_title="CDC Provisional Natality Dashboard",
        page_icon="👶",
        layout="wide"
    )

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
