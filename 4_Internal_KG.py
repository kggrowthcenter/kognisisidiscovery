import pandas as pd
import streamlit as st
import plotly.express as px
from data_processing import finalize_data
from datetime import datetime

# Set the title and favicon in the browser tab
st.set_page_config(page_title='Internal KG', page_icon='👥')

# Retrieve data from data_processing
df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()

# Display logo at the top of the sidebar
st.logo('kognisi_logo.png')

# Header with logos
col1, col2, col3 = st.columns([12, 1, 3])
with col1:
    st.markdown("<h2 style='text-align: center;'>👥 Internal KG</h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')

# Fungsi untuk memuat dan memproses data dengan caching
@st.cache_data
def load_and_process_data():
    # Mengambil dan memproses data
    df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()

# Memuat data dengan caching
merged_df = load_and_process_data()

# Memfilter data untuk pengguna internal
internal_df = df_merged[df_merged['status_learner'] == 'Internal']

# Dropdown untuk memilih Bundle Name tanpa opsi "All"
bundle_names = internal_df['title'].dropna().unique()
selected_bundle = st.sidebar.selectbox("Select Bundle Name", bundle_names)

# Memfilter nama tes berdasarkan Bundle Name yang terkait dengan platform Discovery
test_name_options = internal_df[
    (internal_df['title'] == selected_bundle) & 
    (internal_df['platform'] == 'Discovery')
]['Test Name'].dropna().unique()

if test_name_options.size == 0:
    st.sidebar.warning("No Test Names available for the selected Bundle Name in the Discovery platform.")
else:
    selected_test = st.sidebar.selectbox("Select Test Name", test_name_options)

# Menerapkan filter
internal_df = internal_df[internal_df['title'] == selected_bundle]
internal_df = internal_df[internal_df['Test Name'] == selected_test]

# Treemap untuk jumlah peserta tes per unit
treemap_data = internal_df.groupby(['Test Name', 'unit']).size().reset_index(name='Unit Count')
fig3 = px.treemap(
    treemap_data, 
    title='Test Taker Per Unit', 
    path=["Test Name", "unit"], 
    values="Unit Count", 
    hover_data=["Unit Count"],
    color="unit"
)
fig3.update_traces(textinfo='label+value', hovertemplate='<b>%{label}</b><br>User : %{value}')
fig3.update_layout(width=400, height=650)
st.plotly_chart(fig3, use_container_width=True)

# Diagram lingkaran untuk distribusi typology
typology_counts = internal_df['typology'].value_counts().reset_index()
typology_counts.columns = ['typology', 'User Count']
typology_counts = typology_counts.sort_values(by='User Count', ascending=False)
fig_typology = px.pie(
    typology_counts, 
    names='typology', 
    values='User Count', 
    title='Overall Results'
)
fig_typology.update_traces(
    hovertemplate='<b>%{label}</b><br>%{value}',
    textinfo='percent'
)
fig_typology.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_typology, use_container_width=True)

# Diagram batang bertumpuk untuk hasil per unit
# Grouping by unit and typology, counting users
typology_counts = internal_df.groupby(['unit', 'typology']).size().reset_index(name='User Count')

# Sorting units by total user count
unit_total_counts = typology_counts.groupby('unit')['User Count'].sum().reset_index()
unit_total_counts = unit_total_counts.sort_values(by='User Count', ascending=False)
sorted_units = unit_total_counts['unit']

# Creating the stacked bar chart
fig_stacked = px.bar(
    typology_counts,
    x='unit',
    y='User Count',  # No percentage, using actual user count
    color='typology',
    title='Result Per Unit',
    labels={'User Count': 'User Count'},  # Update label to show actual counts
    text='User Count',
    height=400
)

# Updating layout to stack bars
fig_stacked.update_layout(
    barmode='stack',  # Stacked bars
    xaxis_title='Unit',
    yaxis_title='User Count',  # Updated y-axis label to reflect actual counts
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_units,  # Sorting units by total count
    yaxis=dict(tickformat=',', title='User Count')  # Ensure y-axis shows raw counts
)

# Updating traces to show raw user count in the bars
fig_stacked.update_traces(texttemplate='%{text:.0f}')  # Display raw count in the bars
st.plotly_chart(fig_stacked, use_container_width=True)

# Diagram batang bertumpuk untuk gender berdasarkan count
gender_counts = internal_df.groupby(['gender', 'typology']).size().reset_index(name='User Count')
gender_total_counts = gender_counts.groupby('gender')['User Count'].sum().reset_index()
gender_total_counts = gender_total_counts.sort_values(by='User Count', ascending=False)
sorted_genders = gender_total_counts['gender']

fig_gender = px.bar(
    gender_counts,
    x='gender',
    y='User Count',
    color='typology',
    title='Result Per Gender',
    labels={'User Count': 'User Count'},
    text='User Count',
    height=400
)
fig_gender.update_layout(
    barmode='stack',
    xaxis_title='Gender',
    yaxis_title='User Count',
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_genders,
    yaxis=dict(tickformat=',', title='User Count')
)
fig_gender.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_gender, use_container_width=True)

# Diagram batang bertumpuk untuk generasi berdasarkan count
generation_counts = internal_df.groupby(['generation', 'typology']).size().reset_index(name='User Count')
generation_total_counts = generation_counts.groupby('generation')['User Count'].sum().reset_index()
generation_total_counts = generation_total_counts.sort_values(by='User Count', ascending=False)
sorted_generations = generation_total_counts['generation']

fig_generation = px.bar(
    generation_counts,
    x='generation',
    y='User Count',
    color='typology',
    title='Result Per Generation',
    labels={'User Count': 'User Count'},
    text='User Count',
    height=400
)
fig_generation.update_layout(
    barmode='stack',
    xaxis_title='Generation',
    yaxis_title='User Count',
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_generations,
    yaxis=dict(tickformat=',', title='User Count')
)
fig_generation.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_generation, use_container_width=True)

# Diagram batang bertumpuk untuk layer berdasarkan count
layer_counts = internal_df.groupby(['layer', 'typology']).size().reset_index(name='User Count')
layer_total_counts = layer_counts.groupby('layer')['User Count'].sum().reset_index()
layer_total_counts = layer_total_counts.sort_values(by='User Count', ascending=False)
sorted_layers = layer_total_counts['layer']

fig_layer = px.bar(
    layer_counts,
    x='layer',
    y='User Count',
    color='typology',
    title='Result Per Layer',
    labels={'User Count': 'User Count'},
    text='User Count',
    height=400
)
fig_layer.update_layout(
    barmode='stack',
    xaxis_title='Layer',
    yaxis_title='User Count',
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_layers,
    yaxis=dict(tickformat=',', title='User Count')
)
fig_layer.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_layer, use_container_width=True)
