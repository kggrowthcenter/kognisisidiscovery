import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data
from datetime import datetime

# Set the title and favicon in the browser tab
st.set_page_config(page_title='Result Traits Summary', page_icon='📊')

# Retrieve data from data_processing
df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()

# Display logo at the top of the sidebar
st.logo('kognisi_logo.png')

# Header with logos
col1, col2, col3 = st.columns([12, 1, 3])
with col1:
    st.markdown("<h2 style='text-align: center;'>📊 Result Traits Summary</h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')

# Sidebar filters
st.sidebar.header('Filters')
platform_options = ['All'] + df_merged['platform'].unique().tolist()
selected_platform = st.sidebar.selectbox('Select Platform', platform_options, index=0)

# Filter the data based on the selected platform for dynamic options
filtered_platform_df = df_merged if selected_platform == 'All' else df_merged[df_merged['platform'] == selected_platform]

# Sidebar filters
unit_options = filtered_platform_df['unit'].unique().tolist()
selected_units = st.sidebar.multiselect('Select Unit', unit_options)

layer_options = filtered_platform_df['layer'].unique().tolist()
selected_layers = st.sidebar.multiselect('Select Layer', layer_options)

status_options = ['All'] + filtered_platform_df['status_learner'].unique().tolist()
selected_status = st.sidebar.selectbox('Select Status Learner', status_options)

title_options = filtered_platform_df['title'].unique().tolist()
selected_titles = st.sidebar.multiselect('Select Title', title_options)

company_options = filtered_platform_df['Company'].unique().tolist()
selected_company = st.sidebar.multiselect('Select Company', company_options)

# Date filter setup
min_value, max_value = df_merged['last_updated'].min(), df_merged['last_updated'].max()

# Initialize session state for date filters
if 'from_date' not in st.session_state:
    st.session_state.from_date, st.session_state.to_date = min_value, max_value

# Shortcut buttons for date selection
st.write("**Choose the data period:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Lifetime'):
        st.session_state.from_date, st.session_state.to_date = min_value, max_value
with col2:
    if st.button('This Year'):
        current_year = datetime.now().year
        st.session_state.from_date, st.session_state.to_date = datetime(current_year, 1, 1).date(), datetime.now().date()
with col3:
    if st.button('This Month'):
        current_year, current_month = datetime.now().year, datetime.now().month
        st.session_state.from_date, st.session_state.to_date = datetime(current_year, current_month, 1).date(), datetime.now().date()

# Ensure date selections are within valid range
st.session_state.from_date = max(st.session_state.from_date, min_value)
st.session_state.to_date = min(st.session_state.to_date, max_value)

# Manual date input
from_date, to_date = st.date_input(
    '**Or pick the date manually:**',
    value=(st.session_state.from_date, st.session_state.to_date),
    min_value=min_value,
    max_value=max_value
)

# Update session state with manual input
st.session_state.from_date, st.session_state.to_date = from_date, to_date

# Data filtering based on selected filters
filtered_df = df_merged[
    (df_merged['last_updated'] <= to_date) & 
    (df_merged['last_updated'] >= from_date)
]

if selected_platform != 'All':
    filtered_df = filtered_df[filtered_df['platform'] == selected_platform]
if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['status_learner'] == selected_status]
if selected_units:
    filtered_df = filtered_df[filtered_df['unit'].isin(selected_units)]
if selected_layers:
    filtered_df = filtered_df[filtered_df['layer'].isin(selected_layers)]
if selected_titles:
    filtered_df = filtered_df[filtered_df['title'].isin(selected_titles)]
if selected_company:
    filtered_df = filtered_df[filtered_df['Company'].isin(selected_company)]

# Display horizontal stacked bar chart of platform per unit if 'All' is selected for platform
if selected_platform == 'All':
    st.write("### Platform Distribution")
    
    # Group data to calculate counts and unique emails
    platform_unit_df = (
        filtered_df.groupby(['unit', 'platform'])
        .agg(count=('email', 'size'), Active_Learners=('email', 'nunique'))
        .reset_index()
    )

    # Calculate total counts per unit
    platform_unit_df['total'] = platform_unit_df.groupby('unit')['count'].transform('sum')
    platform_unit_df['percent'] = platform_unit_df['count'] / platform_unit_df['total'] * 100

    # Sort units by total count of all platforms
    sorted_units = (
        platform_unit_df.groupby('unit')['count']
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Create the 100% stacked horizontal bar chart with count labels
    platform_unit_chart = (
        alt.Chart(platform_unit_df)
        .mark_bar()
        .encode(
            y=alt.Y('unit:N', sort=sorted_units, title='Unit'),
            x=alt.X('percent:Q', stack="normalize", title='Percentage (%)'),
            color=alt.Color('platform:N', title='Platform'),
            tooltip=['platform', 'unit', 'Active_Learners']
        )
        .properties(width=600, height=400)
    )

    # Combine the bar chart and the text labels
    st.altair_chart(platform_unit_chart, use_container_width=True)
    
    # Data download for Growth Inventory
    with st.expander("Data Distribution Platform"):
        st.write(platform_unit_df)
        csv = platform_unit_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Distribution_Platform.csv", mime="text/csv", help='Click here to download the data as a CSV file')

    
# Active Users section for Discovery
if selected_platform == 'Discovery':
    st.header('Active Learners - Discovery', divider='gray')
    total_count = filtered_df['email'].nunique()
    internal_count = filtered_df[filtered_df['status_learner'] == 'Internal']['Customer ID'].nunique()
    external_count = filtered_df[filtered_df['status_learner'] == 'External']['Customer ID'].nunique()

    # Display metrics columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Overall: <span style='color: red;'>{total_count:,}</span></strong></p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Internal User: <span style='color: red;'>{internal_count:,}</span></strong></p>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>External User: <span style='color: red;'>{external_count:,}</span></strong></p>", unsafe_allow_html=True)

    # Active learners by bundle_name
    bundle_names = ['GI', 'LEAN', 'ELITE', 'Genuine', 'Astaka']
    if 'title' in filtered_df.columns:
        # Group by bundle_name and count unique Customer IDs
        df_active_learners = filtered_df.groupby(['Customer ID', 'title']).size().reset_index(name='test_count')
        bundle_counts = {bundle: df_active_learners[df_active_learners['title'] == bundle]['Customer ID'].nunique() for bundle in bundle_names}

        # Display active learners counts
        st.markdown("<h3>ACTIVE LEARNERS by Bundle</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, bundle in enumerate(bundle_names):
            with eval(f'col{i + 1}'):
                st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>{bundle}: <span style='color: red;'>{bundle_counts.get(bundle, 0):,}</span></strong></p>", unsafe_allow_html=True)

        # Create bar chart for top bundles
        bundle_chart_data = pd.DataFrame.from_dict(bundle_counts, orient='index', columns=['count']).reset_index()
        bundle_chart_data.columns = ['Bundle', 'Active Learners']

        # Create the bar chart using Altair
        # Stacked bar chart for Growth Inventory
        st.subheader("Top Test Discovery")
        bundle_bar_chart = (
            alt.Chart(bundle_chart_data)
            .mark_bar()
            .encode(
                x=alt.X('Active Learners:Q', title='Active Learners Count'),
                y=alt.Y('Bundle:N', title='Bundle', sort='-x'),
                color=alt.Color('Bundle:N', title='Bundle'),
                tooltip=['Bundle:N', 'Active Learners:Q']
            )
            .properties(width=600, height=400)
        )

        # Display the chart
        st.altair_chart(bundle_bar_chart, use_container_width=True)

        # Data download for Top Test Discovery
        with st.expander("Top Test Discovery"):
            st.write(bundle_chart_data)
            csv = bundle_chart_data.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Top_Test_Discovery.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        
        # Active learners data for Bundle GI
        gi_active_learners = filtered_df[filtered_df['title'] == 'GI']

        # Get highest scores
        highest_scores = gi_active_learners.loc[gi_active_learners.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        gi_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

        # Stacked bar chart for Growth Inventory
        st.subheader("Growth Inventory")
        gi_filtered = filtered_df[filtered_df['title'] == 'GI']
        gi_distribution = gi_filtered.groupby(['Test Name', 'typology']).agg({'Customer ID': 'nunique'}).reset_index()
        gi_distribution.columns = ['Test Name', 'typology', 'Active Users']

        # Calculate percentages
        total_active_users_per_test = gi_distribution.groupby('Test Name')['Active Users'].transform('sum')
        gi_distribution['Percentage'] = (gi_distribution['Active Users'] / total_active_users_per_test * 100).round(2)

        # Plot chart
        chart = alt.Chart(gi_distribution).mark_bar().encode(
            x='Test Name',
            y='Active Users',
            color='typology',
            tooltip=[
                alt.Tooltip('Test Name:N', title='Test Name'),
                alt.Tooltip('typology:N', title='Typology'),
                alt.Tooltip('Active Users:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=600,
            height=400
        ).configure_mark(
            opacity=0.8
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(chart, use_container_width=True)

        # Data download for Growth Inventory
        with st.expander("Data Growth Inventory"):
            st.write(gi_distribution)
            csv = gi_distribution.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Growth_Inventory.csv", mime="text/csv", help='Click here to download the data as a CSV file')


        # Repeat for LEAN
        lean_active_learners = filtered_df[filtered_df['title'] == 'LEAN']

        # Get highest scores for LEAN
        highest_scores_lean = lean_active_learners.loc[lean_active_learners.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        lean_active_learners_data = highest_scores_lean[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

        # Stacked bar chart for LEAN
        st.subheader("LEAN")
        lean_filtered = filtered_df[filtered_df['title'] == 'LEAN']
        lean_distribution = lean_filtered.groupby(['Test Name', 'typology']).agg({'Customer ID': 'nunique'}).reset_index()
        lean_distribution.columns = ['Test Name', 'typology', 'Active Users']

        # Calculate percentages for LEAN
        total_active_users_per_test_lean = lean_distribution.groupby('Test Name')['Active Users'].transform('sum')
        lean_distribution['Percentage'] = (lean_distribution['Active Users'] / total_active_users_per_test_lean * 100).round(2)

        # Plot chart for LEAN
        chart_lean = alt.Chart(lean_distribution).mark_bar().encode(
            x='Test Name',
            y='Active Users',
            color='typology',
            tooltip=[
                alt.Tooltip('Test Name:N', title='Test Name'),
                alt.Tooltip('typology:N', title='Typology'),
                alt.Tooltip('Active Users:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=600,
            height=400
        ).configure_mark(
            opacity=0.8
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(chart_lean, use_container_width=True)

        # Data download for LEAN
        with st.expander("Data LEAN"):
            st.write(lean_distribution)
            csv_lean = lean_distribution.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv_lean, file_name="LEAN.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        # Display final result distribution
        st.subheader("FINAL RESULT LEAN")
        lean_active_learners = filtered_df[filtered_df['title'] == 'LEAN']

        # Get highest scores for LEAN
        highest_scores_lean = lean_active_learners.loc[lean_active_learners.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        lean_active_learners_data = highest_scores_lean[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]
        
        # Get unique combinations of Customer ID and Test Date
        unique_combinations = lean_active_learners_data[['Customer ID', 'last_updated']].drop_duplicates()

        # Merge back to get final_result
        unique_results = unique_combinations.merge(lean_active_learners_data[['Customer ID', 'last_updated', 'final_result']],
                                                   on=['Customer ID', 'last_updated'], 
                                                   how='left').drop_duplicates()

        # Aggregate final_result for pie chart
        final_result_counts = unique_results['final_result'].value_counts().reset_index()
        final_result_counts.columns = ['Final Result', 'Count']

        # Calculate percentage
        final_result_counts['Percentage'] = (final_result_counts['Count'] / final_result_counts['Count'].sum()) * 100

        # Plot pie chart for final results
        pie_chart = alt.Chart(final_result_counts).mark_arc().encode(
            theta='Count:Q',
            color='Final Result:N',
            tooltip=[
                alt.Tooltip('Final Result:N', title='Final Result'),
                alt.Tooltip('Count:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=400,
            height=400
        )

        st.altair_chart(pie_chart, use_container_width=True)

        # Expander for final result data
        with st.expander("View Final Result Data"):
            st.write(final_result_counts)
            csv_final = final_result_counts.to_csv(index=False).encode('utf-8')  # Convert to CSV
            st.download_button(
                label="Download Final Result Data", 
                data=csv_final, 
                file_name="Final_Results_LEAN.csv", 
                mime="text/csv",
                help='Click here to download the final result data as a CSV file'
        )

        # Repeat for ELITE
        elite_active_learners = filtered_df[filtered_df['title'] == 'ELITE']

        # Get highest scores for ELITE
        highest_scores_elite = elite_active_learners.loc[elite_active_learners.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        elite_active_learners_data = highest_scores_elite[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

        # Stacked bar chart for ELITE
        st.subheader("ELITE")
        elite_filtered = filtered_df[filtered_df['title'] == 'ELITE']
        elite_distribution = elite_filtered.groupby(['Test Name', 'typology']).agg({'Customer ID': 'nunique'}).reset_index()
        elite_distribution.columns = ['Test Name', 'typology', 'Active Users']

        # Calculate percentages for ELITE
        total_active_users_per_test_elite = elite_distribution.groupby('Test Name')['Active Users'].transform('sum')
        elite_distribution['Percentage'] = (elite_distribution['Active Users'] / total_active_users_per_test_elite * 100).round(2)

        # Plot chart for ELITE
        chart_elite = alt.Chart(elite_distribution).mark_bar().encode(
            x='Test Name',
            y='Active Users',
            color='typology',
            tooltip=[
                alt.Tooltip('Test Name:N', title='Test Name'),
                alt.Tooltip('typology:N', title='Typology'),
                alt.Tooltip('Active Users:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=600,
            height=400
        ).configure_mark(
            opacity=0.8
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(chart_elite, use_container_width=True)

        # Data download for ELITE
        with st.expander("Data ELITE"):
            st.write(elite_distribution)
            csv_elite = elite_distribution.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv_elite, file_name="ELITE.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        # Display final result distribution
        st.subheader("FINAL RESULT ELITE")
        elite_active_learners = filtered_df[filtered_df['title'] == 'ELITE']

        # Get highest scores for ELITE
        highest_scores_elite = elite_active_learners.loc[elite_active_learners.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        elite_active_learners_data = highest_scores_elite[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]
        
        # Get unique combinations of Customer ID and Test Date
        unique_combinations = elite_active_learners_data[['Customer ID', 'last_updated']].drop_duplicates()

        # Merge back to get final_result
        unique_results = unique_combinations.merge(elite_active_learners_data[['Customer ID', 'last_updated', 'final_result']],
                                                   on=['Customer ID', 'last_updated'], 
                                                   how='left').drop_duplicates()

        # Aggregate final_result for pie chart
        final_result_counts = unique_results['final_result'].value_counts().reset_index()
        final_result_counts.columns = ['Final Result', 'Count']

        # Calculate percentage
        final_result_counts['Percentage'] = (final_result_counts['Count'] / final_result_counts['Count'].sum()) * 100

        # Plot pie chart for final results
        pie_chart = alt.Chart(final_result_counts).mark_arc().encode(
            theta='Count:Q',
            color='Final Result:N',
            tooltip=[
                alt.Tooltip('Final Result:N', title='Final Result'),
                alt.Tooltip('Count:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=400,
            height=400
        )

        st.altair_chart(pie_chart, use_container_width=True)

        # Expander for final result data
        with st.expander("View Final Result Data"):
            st.write(final_result_counts)
            csv_final = final_result_counts.to_csv(index=False).encode('utf-8')  # Convert to CSV
            st.download_button(
                label="Download Final Result Data", 
                data=csv_final, 
                file_name="Final_Results_ELITE.csv", 
                mime="text/csv",
                help='Click here to download the final result data as a CSV file'
        )
            
        st.subheader("Genuine")
        # Filter DataFrame untuk bundle_name yang spesifik
        genuine_filtered = filtered_df[filtered_df['title'] == 'Genuine']

        # Get highest scores
        highest_scores = genuine_filtered.loc[genuine_filtered.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        genuine_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

        # Add a rank column from 1 to 9 based on total_score for each Customer ID and Test Date
        genuine_active_learners_data['rank'] = genuine_active_learners_data.groupby(['Customer ID', 'last_updated'])['total_score'].rank(ascending=False, method='first').astype(int)

        # Filter ranks from 1 to 9
        genuine_active_learners_data = genuine_active_learners_data[genuine_active_learners_data['rank'] <= 9]

        # Create a select box for rank selection with a unique key
        genuine_rank = st.selectbox("Select Top for Genuine", options=list(range(1, 10)), key='genuine_rank_select')

        # Filter data based on the selected rank
        filtered_rank_data = genuine_active_learners_data[genuine_active_learners_data['rank'] == genuine_rank]

        # Count the number of unique users for each test name at the selected rank
        user_count_by_test = filtered_rank_data.groupby('Test Name')['Customer ID'].nunique().reset_index()
        user_count_by_test.columns = ['Test Name', 'Total Active Users']

        # Display the results
        st.write(f"Genuine Top {genuine_rank}")
        st.dataframe(user_count_by_test)

        st.subheader("Astaka")
        # Filter DataFrame untuk bundle_name yang spesifik
        astaka_filtered = filtered_df[filtered_df['title'] == 'Astaka']

        # Get highest scores
        highest_scores = astaka_filtered.loc[astaka_filtered.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
        astaka_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']]

        # Add a rank column from 1 to 6 based on total_score for each Customer ID and Test Date
        astaka_active_learners_data['rank'] = astaka_active_learners_data.groupby(['Customer ID', 'last_updated'])['total_score'].rank(ascending=False, method='first').astype(int)

        # Filter ranks from 1 to 6
        astaka_active_learners_data = astaka_active_learners_data[astaka_active_learners_data['rank'] <= 6]

        # Create a select box for rank selection with a unique key
        astaka_rank = st.selectbox("Select Top for Astaka", options=list(range(1, 7)), key='astaka_rank_select')

        # Filter data based on the selected rank
        filtered_rank_data = astaka_active_learners_data[astaka_active_learners_data['rank'] == astaka_rank]

        # Count the number of unique users for each test name at the selected rank
        user_count_by_test = filtered_rank_data.groupby('Test Name')['Customer ID'].nunique().reset_index()
        user_count_by_test.columns = ['Test Name', 'Total Active Users']

        # Display the results
        st.write(f"Astaka Top {astaka_rank}")
        st.dataframe(user_count_by_test)

if selected_platform == 'Capture':
    st.header('Active Learners - Capture', divider='gray')
    total_count = filtered_df['email'].nunique()
    internal_count = filtered_df[filtered_df['status_learner'] == 'Internal']['email'].nunique()
    external_count = filtered_df[filtered_df['status_learner'] == 'External']['email'].nunique()

    # Display metrics columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Overall: <span style='color: red;'>{total_count:,}</span></strong></p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Internal User: <span style='color: red;'>{internal_count:,}</span></strong></p>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>External User: <span style='color: red;'>{external_count:,}</span></strong></p>", unsafe_allow_html=True)

    # Count unique emails per title
    title_counts = filtered_df.groupby('title')['email'].nunique().reset_index()
    title_counts.columns = ['title', 'active_learners']

    # Sort the data from highest to lowest
    title_counts = title_counts.sort_values(by='active_learners', ascending=False)

    # Create the bar chart
    chart = alt.Chart(title_counts).mark_bar().encode(
        x=alt.X('active_learners:Q', title='Active Learners'),
        y=alt.Y('title:O', title='Title', sort=alt.EncodingSortField(field='active_learners', order='descending')),
        color=alt.Color('title:O', scale=alt.Scale(scheme='category10')),
        tooltip=['title', 'active_learners']
    ).properties(
        title='Active Learners by Title'
    )

    # Add text layer to display active learners count on top of bars
    text = chart.mark_text(
        align='left',
        baseline='middle',
        color='black',
        fontSize=12,
        fontWeight='bold',
        dy=-5 # Adjusts the vertical position of the text
    ).encode(
        text='active_learners:Q'
    )
    
    # Combine the bar chart and text layer
    final_chart = chart + text

    # Display the chart
    st.altair_chart(final_chart, use_container_width=True)

    # Data download for Top Test Capture
    with st.expander("Top Test Capture"):
        st.write(title_counts)  # Now includes unit information
        csv = title_counts.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Data", 
            data=csv, 
            file_name="Top_Test_Capture.csv", 
            mime="text/csv", 
            help='Click here to download the data as a CSV file'
        )
