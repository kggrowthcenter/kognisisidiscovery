import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data
from datetime import datetime

# Set the title and favicon in the browser tab
st.set_page_config(page_title='Demography', page_icon='🌍')

# Retrieve data from data_processing
df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()
st.dataframe (df_merged)

# Display logo at the top of the sidebar
st.logo('kognisi_logo.png')

# Header with logos
col1, col2, col3 = st.columns([12, 1, 3])
with col1:
    st.markdown("<h2 style='text-align: center;'>🌍 Demography </h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')
