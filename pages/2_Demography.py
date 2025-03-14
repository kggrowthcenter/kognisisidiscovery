import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data
from datetime import datetime

# Set the title and favicon in the browser tab
st.set_page_config(page_title='Demography', page_icon='🌍')

# Retrieve data from data_processing
df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()

# Display logo at the top of the sidebar
st.logo('kognisi_logo.png')

# Header with logos
col1, col2, col3 = st.columns([12, 1, 3])
with col1:
    st.markdown("<h2 style='text-align: center;'>🌍 Demography </h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')

# Sidebar filters
platform_options = ['All'] + sorted(df_merged['platform'].unique().tolist())
selected_platform = st.sidebar.selectbox('Select Platform', platform_options)

unit_options = sorted(df_merged['unit'].unique().tolist())
selected_unit = st.sidebar.multiselect('Select Unit', unit_options)

layer_options = sorted(df_merged['layer'].astype(str).unique().tolist())
#layer_options = sorted(df_merged['layer'].unique().tolist())
selected_layer = st.sidebar.multiselect('Select Layer', layer_options)

status_options = ['All'] + sorted(df_merged['status_learner'].unique().tolist())
selected_status = st.sidebar.selectbox('Select Status Learner', status_options)

title_options = sorted(df_merged['title'].unique().tolist())
selected_title = st.sidebar.multiselect('Select Title', title_options)

company_options = sorted(df_merged['Company'].unique().tolist())
selected_company = st.sidebar.multiselect('Select Company', company_options)

institution_options = sorted(df_merged['institution'].unique().tolist())
selected_institution = st.sidebar.multiselect('Select Institution', institution_options)

# Main title and description
st.markdown('''  
In the Active Learners Growth Discovery - Capture, the key user metrics include: 
1. **Overall**: Users test on the Discovery and Capture platforms. 
2. **Internal User**: Active learners who are Kompas Gramedia Group employees. 
3. **External User**: Active learners who are not Kompas Gramedia Group employees.
''')
st.markdown('---')

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

# Data filtering based on selected dates and platform
filtered_df = df_merged[
    (df_merged['last_updated'] >= from_date) & 
    (df_merged['last_updated'] <= to_date)
]

if selected_platform != 'All':
    filtered_df = filtered_df[filtered_df['platform'] == selected_platform]

if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['status_learner'] == selected_status]

if selected_unit:
    filtered_df = filtered_df[filtered_df['unit'].isin(selected_unit)]

if selected_layer:
    filtered_df = filtered_df[filtered_df['layer'].isin(selected_layer)]

if selected_title:
    filtered_df = filtered_df[filtered_df['title'].isin(selected_title)]

if selected_company:
    filtered_df = filtered_df[filtered_df['Company'].isin(selected_company)]

if selected_institution:
    filtered_df = filtered_df[filtered_df['institution'].isin(selected_institution)]

# Active Users section
st.header('Active Learners', divider='gray')
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

# Register User Distribution
st.subheader('Test Date Distribution', divider='gray')

# Count unique active learners by test date
active_learners_counts = (filtered_df
    .groupby('last_updated')
    .agg(active_learners=('email', 'nunique'))
    .reset_index())

# Create a line chart for active learners
line_chart = alt.Chart(active_learners_counts).mark_line(
    stroke='steelblue',  
    strokeWidth=2  
).encode(
    x=alt.X('last_updated:T', title='Test Date', axis=alt.Axis(format='%Y-%m-%d', labelAngle=-45)),
    y=alt.Y('active_learners:Q', title='Active Learners', axis=alt.Axis(titleColor='black')),
    tooltip=[
        alt.Tooltip('last_updated:T', title='Test Date', format='%Y-%m-%d'), 
        alt.Tooltip('active_learners:Q', title='Active Learners')
    ]
).properties(width=600, height=400)

# Display the chart
st.altair_chart(line_chart, use_container_width=True)

# Active learners data table
with st.expander("View Active Learners Breakdown"):
    st.dataframe(active_learners_counts)

# Demography Breakdown
st.subheader('Demography Breakdown', divider='gray')
breakdown_options = ['Unit', 'Layer', 'Gender', 'Company', 'Generation', 'Institution', 'Last Education', 'Province']
selected_breakdown = st.selectbox('Select Demographic Breakdown:', breakdown_options)

# Helper function to create a bar chart with text
def create_bar_chart_with_text(data, x_col, y_col, title):
    bar_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(f'{x_col}:Q', title='Active Learners'),
        y=alt.Y(f'{y_col}:O', title=title, sort='-x'),
        tooltip=[
            alt.Tooltip(f'{y_col}:O', title=title),
            alt.Tooltip(f'{x_col}:Q', title='Active Learners')
        ]
    ).properties(width=600, height=400)

    # Add text layer
    text = bar_chart.mark_text(
        align='left',
        fontWeight='bold',
        baseline='middle',
        dx=3
    ).encode(
        text=alt.Text(f'{x_col}:Q', format=',')
    )

    return bar_chart + text

# Mapping for demographic breakdown
breakdown_mapping = {
    'Unit': 'unit',
    'Layer': 'layer',
    'Gender': 'gender',
    'Generation': 'generation',
    'Institution': 'institution',
    'Last Education': 'last_education',
    'Company': 'Company',
    'Province': 'Province'
}

# Clean data in the Company column
filtered_df.loc[:, 'Company'] = filtered_df['Company'].replace(
    ['-', '.', '0', 'n/a', 'N/a', 'NA'], 'N/A', regex=False
)

# Process selected breakdown
if selected_breakdown in breakdown_mapping:
    breakdown_column = breakdown_mapping[selected_breakdown]

    # Calculate active learners
    counts = (
        filtered_df
        .groupby(['status_learner', breakdown_column])
        .agg(active_learners=('email', 'nunique'))
        .reset_index()
    )

    # Handle specific breakdowns
    if selected_breakdown in ['Unit', 'Generation']:
        counts = counts.groupby([breakdown_column, 'status_learner']).agg({'active_learners': 'sum'}).reset_index()
        chart_title = f'Breakdown by {selected_breakdown}'
        chart = create_bar_chart_with_text(counts, 'active_learners', breakdown_column, chart_title)
        st.altair_chart(chart, use_container_width=True)

    elif selected_breakdown == 'Layer':
        counts = counts.groupby([breakdown_column, 'status_learner']).agg({'active_learners': 'sum'}).reset_index()
        total_counts = counts.groupby(breakdown_column).agg(total_active_learners=('active_learners', 'sum')).reset_index()
        counts = counts.merge(total_counts, on=breakdown_column)
        counts['percentage'] = (counts['active_learners'] / counts['total_active_learners']) * 100
        counts = counts.sort_values(by='total_active_learners', ascending=False)

        # Stacked bar chart
        stacked_bar_chart = alt.Chart(counts).mark_bar().encode(
            x=alt.X('percentage:Q', title='Active Learners (%)'),
            y=alt.Y(
                f'{breakdown_column}:N',
                title=selected_breakdown,
                sort='-x'
            ),
            color=alt.Color(
                'status_learner:N',
                title='User Type',
                scale=alt.Scale(domain=['Internal', 'External'], range=['blue', 'orange'])
            ),
            tooltip=[
                alt.Tooltip(f'{breakdown_column}:N', title=selected_breakdown),
                alt.Tooltip('active_learners:Q', title='Active Learners'),
                alt.Tooltip('status_learner:N', title='Status Learner')
            ]
        ).properties(width=600, height=400)

        st.altair_chart(stacked_bar_chart, use_container_width=True)

    elif selected_breakdown in ['Institution', 'Company', 'Last Education', 'Province']:
        # Calculate total active learners and handle top 10 filtering
        total_counts = counts.groupby(breakdown_column).agg(
            total_active_learners=('active_learners', 'sum')
        ).reset_index()

        counts = counts.merge(total_counts, on=breakdown_column)
        counts = counts.sort_values(by='total_active_learners', ascending=False).head(10)

        if selected_status == 'All':
            # Stacked bar chart (100%)
            counts['percentage'] = (counts['active_learners'] / counts['total_active_learners']) * 100
            chart = alt.Chart(counts).mark_bar().encode(
                x=alt.X('percentage:Q', title='Active Learners (%)'),
                y=alt.Y(
                    f'{breakdown_column}:N',
                    title=selected_breakdown,
                    sort=alt.EncodingSortField(field='total_active_learners', order='descending')
                ),
                color=alt.Color(
                    'status_learner:N',
                    title='User Type',
                    scale=alt.Scale(domain=['Internal', 'External'], range=['blue', 'orange'])
                ),
                tooltip=[
                    alt.Tooltip(f'{breakdown_column}:N', title=selected_breakdown),
                    alt.Tooltip('percentage:Q', title='Percentage of Active Learners'),
                    alt.Tooltip('status_learner:N', title='Status Learner'),
                    alt.Tooltip('active_learners:Q', title='Active Learners')
                ]
            ).properties(width=600, height=400)
            st.altair_chart(chart, use_container_width=True)
        else:
            # Bar chart
            chart = alt.Chart(counts).mark_bar().encode(
                x=alt.X('active_learners:Q', title='Active Learners'),
                y=alt.Y(
                    f'{breakdown_column}:N',
                    title=selected_breakdown,
                    sort=alt.EncodingSortField(field='active_learners', order='descending')
                ),
                color=alt.Color(
                    'status_learner:N',
                    title='User Type',
                    scale=alt.Scale(domain=['Internal', 'External'], range=['blue', 'orange'])
                ),
                tooltip=[
                    alt.Tooltip(f'{breakdown_column}:N', title=selected_breakdown),
                    alt.Tooltip('active_learners:Q', title='Active Learners'),
                    alt.Tooltip('status_learner:N', title='Status Learner')
                ]
            ).properties(width=600, height=400)

            text = chart.mark_text(
                align='left',
                fontWeight='bold',
                baseline='middle',
                color='black',
                size='15',
                dy=3  # Adjust vertical positioning of the text
            ).encode(
                text='active_learners:Q',
                color=alt.value('black')  # Ensure text remains black
            )

            chart = chart + text

            st.altair_chart(chart, use_container_width=True)
    
    elif selected_breakdown == 'Last Education':
        total_counts = counts.groupby(breakdown_column).agg(total_active_learners=('active_learners', 'sum')).reset_index()
        counts = counts.merge(total_counts, on=breakdown_column)
        counts['percentage'] = (counts['active_learners'] / counts['total_active_learners']) * 100
        stacked_bar_chart = alt.Chart(counts).mark_bar().encode(
            x=alt.X('percentage:Q', title='Active Learners (%)'),
            y=alt.Y(f'{breakdown_column}:N', title='Last Education', sort='-x'),
            color=alt.Color('status_learner:N', title='User Type', scale=alt.Scale(domain=['Internal', 'External'], range=['blue', 'orange'])),
            tooltip=[
                alt.Tooltip(f'{breakdown_column}:N', title='Last Education'),
                alt.Tooltip('active_learners:Q', title='Active Learners'),
                alt.Tooltip('percentage:Q', title='Percentage of Active Learners'),
                alt.Tooltip('status_learner:N', title='Status Learner')
            ]
        ).properties(width=600, height=400)
        st.altair_chart(stacked_bar_chart, use_container_width=True)
        with st.expander("View Last Education Breakdown"):
            st.dataframe(counts)

    elif selected_breakdown == 'Gender':
        # filtered_gender_df = filtered_df[filtered_df['gender'] != 'n/a']
        gender_counts = (
            filtered_df
            .groupby(['status_learner', 'gender'])
            .agg(active_learners=('email', 'nunique'))
            .reset_index()
        )

        pie_chart = alt.Chart(gender_counts).mark_arc().encode(
            theta=alt.Theta('active_learners:Q', title='Active Learners'),
            color=alt.Color('gender:N', title='Gender'),
            tooltip=[
                alt.Tooltip('gender:N', title='Gender'),
                alt.Tooltip('active_learners:Q', title='Active Learners')
            ]
        ).properties(width=600, height=400)
        st.altair_chart(pie_chart, use_container_width=True)

    # Display breakdown table
    with st.expander(f"View {selected_breakdown} Breakdown"):
        st.dataframe(counts)
