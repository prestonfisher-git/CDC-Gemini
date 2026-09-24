from pathlib import Path
import pandas as pd
import streamlit as st
from src.utils import STATE_TO_ABBR, MONTH_ORDER

@st.cache_data
def load_data(file_path: str = "Provisional_Natality_2025_CDC1.csv") -> pd.DataFrame:
    """
    Loads natality dataset from local or cloud path, validates columns,
    and formats categorical orders and state postal codes.
    """
    path = Path(file_path)
    if not path.exists():
        # Fallback search for nested data directory
        path = Path("data") / file_path
        if not path.exists():
            st.error(f"Data file '{file_path}' not found.")
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
