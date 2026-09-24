import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

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
