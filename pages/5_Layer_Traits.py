import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data

# Setting page title and favicon
st.set_page_config(page_title='Layer Traits Summary')

# Adding logo and header to the sidebar and main page
st.logo('kognisi_logo.png')
col1, col2, col3 = st.columns([1, 12, 3])
with col2:
    st.markdown("<h2 style='text-align: center;'>KG EMPLOYEE LAYER TRAITS SUMMARY</h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')

# Dashboard guidelines
st.markdown("""
    #### Panduan Layer Traits Summary 
    - **Layer 1** adalah Group 5 Str Layer 1. 
    - **Layer 2** adalah Group 4 Str Layer 2. 
    - **Layer 3** adalah Group 3 Str Layer 3A dan Group 3 Str Layer 3B. 
    - **Layer 4** adalah Group 2 Str Layer 4.
    - **Layer 5** adalah Group 1 Str Layer 5.
    - **Non Struktural** adalah Group 1, Group 2, Group 3, Group 4 dan Group 5 
""")

# Caching function for loading and processing data
@st.cache_data
def load_and_process_data():
    # Load and process data
    df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()
    return df_merged

# Load data with caching
df_merged = load_and_process_data()

# Filter data for internal users
internal_df = df_merged[df_merged['status_learner'] == 'Internal']

# Mapping for grouping layers
layer_mapping = {
    'Group 5 Str Layer 1': 'Layer 1',
    'Group 4 Str Layer 2': 'Layer 2',
    'Group 3 Str Layer 3B': 'Layer 3',
    'Group 3 Str Layer 3A': 'Layer 3',
    'Group 2 Str Layer 4': 'Layer 4',
    'Group 1 Str Layer 5': 'Layer 5',
    'Group 1': 'Non Struktural',
    'Group 2': 'Non Struktural',
    'Group 3': 'Non Struktural',
    'Group 4': 'Non Struktural',
    'Group 5': 'Non Struktural'

}

# Pastikan sebelum ada modifikasi, kita copy dulu datanya
internal_df = internal_df.copy()

# Apply the mapping to create a new column for grouped layers
internal_df.loc[:, 'layer_group'] = internal_df['layer'].map(layer_mapping)

# Sidebar filters with multiselect
st.sidebar.header("Filter Options")
selected_layers = st.sidebar.multiselect(
    "Select Layers",
    options=['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 'Layer 5', 'Non Struktural'],
    default=[]
)

# Filter based on selected layers
df_filtered = internal_df[internal_df['layer_group'].isin(selected_layers)] if selected_layers else internal_df

# Add unit filter to the sidebar
selected_units = st.sidebar.multiselect(
    "Select Unit",
    options=df_filtered['unit'].unique(),
    default=[]
)

# Apply unit filter if units are selected
if selected_units:
    df_filtered = df_filtered[df_filtered['unit'].isin(selected_units)]

# Add subunit filter to the sidebar
selected_subunits = st.sidebar.multiselect(
    "Select Subunit",
    options=df_filtered['subunit'].unique(),
    default=[]
)

# Apply unit filter if units are selected
if selected_subunits:
    df_filtered = df_filtered[df_filtered['subunit'].isin(selected_subunits)]

# Add years filter to the sidebar
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=df_filtered['tenure'].unique(),
    default=[]
)

# Apply unit filter if units are selected
if selected_years:
    df_filtered = df_filtered[df_filtered['tenure'].isin(selected_years)]

# Active learners by bundle
bundle_names = ['GI', 'LEAN', 'ELITE', 'Genuine', 'Astaka']

# Create filtered dataframe for active learners
if 'title' in df_filtered.columns:
    df_active_learners = df_filtered.groupby(['Customer ID', 'last_updated', 'title']).size().reset_index(name='test_count')

    # Count active learners per bundle
    bundle_counts = {bundle: df_active_learners[df_active_learners['title'] == bundle]['Customer ID'].nunique() for bundle in bundle_names}

    # Display active learners counts
    st.markdown("<h3>ACTIVE LEARNERS</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    for i, bundle in enumerate(bundle_names):
        with eval(f'col{i + 1}'):
            st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>{bundle}: <span style='color: red;'>{bundle_counts[bundle]:,}</span></strong></p>", unsafe_allow_html=True)
                

# 1. Get the latest test results for each email and Test Name
latest_test_results = df_filtered.loc[df_filtered.groupby(['email', 'Test Name'])['last_updated'].idxmax()]

# 2. Count participants based on bundle_name
participant_counts = df_filtered.groupby('title')['email'].nunique().reset_index()
participant_counts.columns = ['title', 'jumlah_partisipan']

# 3. Count users based on typology from the latest results
typology_user_counts = latest_test_results.groupby('typology')['email'].nunique().reset_index()
typology_user_counts.columns = ['typology', 'jumlah']

# 4. Get unique Test Name for each bundle_name
test_names = df_filtered[['title', 'Test Name']].drop_duplicates()

# 5. Get all unique typology results for each Test Name
typology_results = latest_test_results.groupby(['Test Name', 'typology'])['email'].nunique().reset_index()
typology_results.columns = ['Test Name', 'typology', 'jumlah']

# 6. Calculate percentages for each typology per Test Name
total_users_per_test = typology_results.groupby('Test Name')['jumlah'].transform('sum')
typology_results['persentase'] = (typology_results['jumlah'] / total_users_per_test * 100).round(2)

# 7. Combine results into one DataFrame
result_df = pd.merge(participant_counts, test_names, on='title', how='left')
result_df = pd.merge(result_df, typology_results, on='Test Name', how='left')

# 8. Add rows for Overall ELITE based on filtered results
final_results_elite = latest_test_results[latest_test_results['title'] == 'ELITE'].groupby('final_result')['email'].nunique().reset_index()
overall_elite_rows = [{
    'title': 'ELITE',
    'jumlah_partisipan': participant_counts.loc[participant_counts['title'] == 'ELITE', 'jumlah_partisipan'].values[0],
    'Test Name': 'Overall ELITE',
    'typology': row['final_result'],
    'jumlah': row['email'],
    'persentase': (row['email'] / participant_counts.loc[participant_counts['title'] == 'ELITE', 'jumlah_partisipan'].values[0] * 100).round(2)
} for _, row in final_results_elite.iterrows()]

overall_elite_df = pd.DataFrame(overall_elite_rows)

# 9. Add rows for Overall LEAN based on filtered results
final_results_lean = latest_test_results[latest_test_results['title'] == 'LEAN'].groupby('final_result')['email'].nunique().reset_index()
overall_lean_rows = [{
    'title': 'LEAN',
    'jumlah_partisipan': participant_counts.loc[participant_counts['title'] == 'LEAN', 'jumlah_partisipan'].values[0],
    'Test Name': 'Overall LEAN',
    'typology': row['final_result'],
    'jumlah': row['email'],
    'persentase': (row['email'] / participant_counts.loc[participant_counts['title'] == 'LEAN', 'jumlah_partisipan'].values[0] * 100).round(2)
} for _, row in final_results_lean.iterrows()]

overall_lean_df = pd.DataFrame(overall_lean_rows)

# 10. Combine result_df with overall_elite_df and overall_lean_df
result_df = pd.concat([result_df, overall_elite_df, overall_lean_df], ignore_index=True)

# 11. Filter for desired bundles: GI, ELITE, LEAN
filtered_bundles = ['GI', 'ELITE', 'LEAN']
result_df = result_df[result_df['title'].isin(filtered_bundles)]

# 12. Set categorical order and sort
result_df['title'] = pd.Categorical(result_df['title'], categories=filtered_bundles, ordered=True)
result_df = result_df.sort_values(['title', 'Test Name']).reset_index(drop=True)

# 13. Combine number of users with result_df without additional calculations
combined_result_df = pd.merge(result_df, typology_user_counts[['typology']], on='typology', how='left')

# 14. Create a custom sort order for 'Test Name'
def custom_sort_order(test_name):
    if test_name in ["Mindset", "Overall ELITE", "Overall LEAN"]:
        return 0
    return 1

combined_result_df['sort_order'] = combined_result_df['Test Name'].apply(custom_sort_order)

# Sort by bundle_name and custom sort order
combined_result_df = combined_result_df.sort_values(['title', 'sort_order', 'Test Name']).reset_index(drop=True)

# 15. Bundle filter
st.sidebar.header("Bundle Name Filter")
selected_bundle = st.sidebar.selectbox("Select Bundle Name", options=filtered_bundles, index=0)

# Filter combined_result_df based on selected bundle
if selected_bundle == 'LEAN':
    # Hapus baris dengan typology 'The Olympian' dan 'The Spectator' untuk bundle LEAN
    combined_result_df = combined_result_df[
        (combined_result_df['title'] == selected_bundle) & 
        (~combined_result_df['typology'].isin(['The Olympian', 'The Spectator']))
    ]
elif selected_bundle == 'ELITE':
    # Hapus baris dengan typology 'Citizen' dan 'Governor' untuk bundle ELITE
    combined_result_df = combined_result_df[
    (combined_result_df['title'] == selected_bundle) & 
    (~combined_result_df['typology'].isin(['Citizen', 'Governor']))
    ]
else:
    # Filter untuk bundle lain
    combined_result_df = combined_result_df[combined_result_df['title'] == selected_bundle]
    
# 16. Display results in Streamlit, excluding 'sort_order'
selected_layers_title = ', '.join(selected_layers) if selected_layers else 'All Layers'
selected_units_title = ', '.join(selected_units) if selected_units else 'All Units'
st.subheader(f"{selected_bundle} Traits Summary for {selected_layers_title} ({selected_units_title})")
st.dataframe(combined_result_df.drop(columns=['sort_order']))

# Menghitung total pengguna untuk setiap Test Name
total_users_per_test = combined_result_df.groupby('Test Name')['jumlah'].transform('sum')

# Menghitung persentase untuk setiap typology pada masing-masing Test Name
combined_result_df['persentase'] = (combined_result_df['jumlah'] / total_users_per_test * 100).round(2)

# Membuat stacked bar chart dengan warna otomatis untuk setiap nilai typology
stacked_bar_chart = alt.Chart(combined_result_df).mark_bar().encode(
    x=alt.X('persentase:Q', title='Persentase Active Learners'),
    y=alt.Y('Test Name:N', title='Test Name', sort='-x'),  # Menggunakan Test Name untuk sumbu Y
    color=alt.Color(
        'typology:N', 
        title='Typology',
        scale=alt.Scale(scheme='category10')  # Palet warna otomatis untuk berbagai nilai typology
    ),
    tooltip=[
        alt.Tooltip('Test Name:N', title='Test Name'), 
        alt.Tooltip('jumlah:Q', title='Jumlah'),
        alt.Tooltip('typology:N', title='Typology'),
        alt.Tooltip('persentase:Q', title='Persentase (%)')
    ]
).properties(
    title=f'Distribusi {selected_layers_title} Berdasarkan traits {selected_bundle} di {selected_units_title}',
    width=600,
    height=400
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
)

# Menampilkan stacked bar chart di Streamlit
st.altair_chart(stacked_bar_chart, use_container_width=True)

# Filter for 'Genuine' bundle
genuine_filtered = df_filtered[df_filtered['title'] == 'Genuine']

# Get the highest scores
highest_scores = genuine_filtered.loc[genuine_filtered.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]

# Select relevant columns for the genuine active learners data
genuine_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

genuine_active_learners_data = genuine_active_learners_data.copy()

# Add a rank column from 1 to 9 based on total_score for each Customer ID and Test Date
genuine_active_learners_data.loc[:, 'rank'] = genuine_active_learners_data.groupby(
    ['Customer ID', 'last_updated']
)['total_score'].rank(ascending=False, method='first').astype(int)

# Filter ranks from 1 to 9
genuine_active_learners_data = genuine_active_learners_data[genuine_active_learners_data['rank'] <= 9]

# Add a select box for filtering by rank
selected_rank = st.selectbox("Select Rank", options=range(1, 10), index=0)

# Filter the data based on the selected rank
filtered_data_by_rank = genuine_active_learners_data[genuine_active_learners_data['rank'] == selected_rank]

# Get the latest Test Date results for each email
latest_results = filtered_data_by_rank.loc[filtered_data_by_rank.groupby('email')['last_updated'].idxmax()]

# Calculate jumlah_partisipan (total unique email for the bundle)
total_participants = latest_results['email'].nunique()

st.subheader(f"Genuine TOP {selected_rank} Traits Summary for {selected_layers_title} ({selected_units_title})")

# Prepare the data for display
summary_data = (
    latest_results
    .groupby(['title', 'Test Name'])  # Group by bundle_name and Test Name
    .agg(
        jumlah_partisipan=('email', 'nunique'),  # Count of unique email based only on Test Name
        jumlah=('email', 'count')  # Count of total entries based on email per Test Name
    )
    .reset_index()
)

# Add the total_participants to the summary_data
summary_data['jumlah_partisipan'] = total_participants

# Calculate the percentage
summary_data['persentase'] = (summary_data['jumlah'] / summary_data['jumlah_partisipan'] * 100).round(2)

# Reorder the columns as specified
summary_data = summary_data[['title', 'jumlah_partisipan', 'Test Name', 'jumlah', 'persentase']]
st.dataframe(summary_data)

# Visualization: Simple bar chart for jumlah
bar_chart = alt.Chart(summary_data).mark_bar().encode(
    x=alt.X('Test Name:O', title='Test Name'),
    y=alt.Y('jumlah:Q', title='Jumlah'),
    tooltip=['Test Name', 'jumlah', 'persentase']
).properties(
    title=f'Distribusi Genuine TOP {selected_rank}'
)

# Display the bar chart
st.altair_chart(bar_chart, use_container_width=True)

# Filter for 'Astaka' bundle
astaka_filtered = df_filtered[df_filtered['title'] == 'Astaka']

# Get the highest scores
highest_scores = astaka_filtered.loc[astaka_filtered.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]

# Select relevant columns for the genuine active learners data
astaka_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

astaka_active_learners_data = astaka_active_learners_data.copy()

# Add a rank column from 1 to 6 based on total_score for each Customer ID and Test Date
astaka_active_learners_data.loc[:, 'rank'] = astaka_active_learners_data.groupby(
    ['Customer ID', 'last_updated']
)['total_score'].rank(ascending=False, method='first').astype(int)

# Filter ranks from 1 to 6
astaka_active_learners_data = astaka_active_learners_data[astaka_active_learners_data['rank'] <= 6]

# Add a select box for filtering by rank
selected_rank = st.selectbox("Select Rank", options=range(1, 7), index=0)

# Filter the data based on the selected rank
filtered_data_by_rank = astaka_active_learners_data[astaka_active_learners_data['rank'] == selected_rank]

# Get the latest Test Date results for each email
latest_results = filtered_data_by_rank.loc[filtered_data_by_rank.groupby('email')['last_updated'].idxmax()]

# Calculate jumlah_partisipan (total unique email for the bundle)
total_participants = latest_results['email'].nunique()

# Prepare the data for display
summary_data = (
    latest_results
    .groupby(['title', 'Test Name'])  # Group by bundle_name and Test Name
    .agg(
        jumlah_partisipan=('email', 'nunique'),  # Count of unique email based only on Test Name
        jumlah=('email', 'count')  # Count of total entries based on email per Test Name
    )
    .reset_index()
)

# Add the total_participants to the summary_data
summary_data['jumlah_partisipan'] = total_participants

# Calculate the percentage
summary_data['persentase'] = (summary_data['jumlah'] / summary_data['jumlah_partisipan'] * 100).round(2)

# Reorder the columns as specified
summary_data = summary_data[['title', 'jumlah_partisipan', 'Test Name', 'jumlah', 'persentase']]

# Display the filtered data in Streamlit
st.subheader(f"Astaka TOP {selected_rank} Traits Summary for {selected_layers_title} ({selected_units_title})")
st.dataframe(summary_data)

# Visualization: Simple bar chart for jumlah
bar_chart = alt.Chart(summary_data).mark_bar().encode(
    x=alt.X('Test Name:O', title='Test Name'),
    y=alt.Y('jumlah:Q', title='Jumlah'),
    tooltip=['Test Name', 'jumlah', 'persentase']
).properties(
    title=f'Distribusi ASTAKA TOP {selected_rank}'
)

# Display the bar chart
st.altair_chart(bar_chart, use_container_width=True)
