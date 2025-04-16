import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data
from datetime import datetime

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='User Growth',
    page_icon='📈',
)

# Return data from data_processing
df_discovery, df_sap, df_merged, df_combined_au_capture, df_capture_sheet3 = finalize_data()

# Display logo at the top of the sidebar
st.logo('kognisi_logo.png')

# Add filters to the sidebar
st.sidebar.header('Filters')

# Filter for Platform
platform_options = ['All'] + df_combined_au_capture['platform'].unique().tolist()
selected_platform = st.sidebar.selectbox('Select Platform', platform_options)

# Filter for Learner Status
status_options = ['All'] + df_combined_au_capture['learner_status'].unique().tolist()
selected_status = st.sidebar.selectbox('Select Status', status_options)

# Set the main title and description
st.markdown(''' 
# 📈 User Growth 

In the User Growth Discovery - Capture, the key user metrics include: 
1. **Overall**: Users who have registered at least one content on one platform. 
2. **Active User**: Users who have accessed at least one content on one platform.
3. **Passive User**: Users who have not accessed any content on any platform.
''')

# Add some spacing
st.markdown('---')

# Tentukan nilai min dan max untuk tanggal
min_value = df_combined_au_capture['created_at'].min()
max_value = df_combined_au_capture['created_at'].max()

# Inisialisasi session state untuk filter tanggal
if 'from_date' not in st.session_state:
    st.session_state.from_date = min_value
if 'to_date' not in st.session_state:
    st.session_state.to_date = max_value

# Tampilkan tombol shortcut untuk filter
st.write("**Choose the data period:**")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Lifetime'):
        st.session_state.from_date = min_value
        st.session_state.to_date = max_value

with col2:
    if st.button('This Year'):
        current_year = datetime.now().year
        st.session_state.from_date = datetime(current_year, 1, 1).date()
        st.session_state.to_date = min(datetime.now().date(), max_value)

with col3:
    if st.button('This Month'):
        current_year = datetime.now().year
        current_month = datetime.now().month
        st.session_state.from_date = datetime(current_year, current_month, 1).date()
        st.session_state.to_date = min(datetime.now().date(), max_value)

# Validasi nilai tanggal untuk menghindari input yang tidak valid
from_date, to_date = st.date_input(
    '**Or pick the date manually:**',
    value=[
        max(st.session_state.from_date, min_value),
        min(st.session_state.to_date, max_value)
    ],
    min_value=min_value,
    max_value=max_value
)

# Perbarui session state
st.session_state.from_date = from_date
st.session_state.to_date = to_date

# Filter data berdasarkan rentang tanggal
filtered_df = df_combined_au_capture[
    (df_combined_au_capture['created_at'] >= from_date) & 
    (df_combined_au_capture['created_at'] <= to_date)
]

# Filter tambahan berdasarkan platform
if selected_platform != 'All':
    filtered_df = filtered_df[filtered_df['platform'] == selected_platform]

# Filter tambahan berdasarkan status pembelajar
if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['learner_status'] == selected_status]

# Active Users section
st.header('Active User', divider='gray')

# Calculate the distinct counts of users based on email
total_count = filtered_df['email'].nunique()  # Total registered users (unique emails)
Active_count = filtered_df[filtered_df['learner_status'] == 'Active']['email'].nunique()  # Unique Active users
Passive_count = filtered_df[filtered_df['learner_status'] == 'Passive']['email'].nunique()  # Unique Ppassive users

# Display metrics column
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Overall: <span style='color: red;'>{total_count:,}</span></strong></p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Active User: <span style='color: red;'>{Active_count:,}</span></strong></p>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Passive User: <span style='color: red;'>{Passive_count:,}</span></strong></p>", unsafe_allow_html=True)

# Register User Distribution
st.subheader('Register User Distribution', divider='gray')

# Create a line chart for active users based on created_at
active_user_counts = (filtered_df
                      .groupby('created_at')
                      .agg(active_users=('email', 'nunique'))
                      .reset_index())

# Create a line chart for active learners
line_chart = alt.Chart(active_user_counts).mark_line(
    stroke='steelblue',  # Change the line color
    strokeWidth=2  # Increase line width for better visibility
).encode(
    x=alt.X('created_at:T', title='Registered Date', 
            axis=alt.Axis(format='%Y-%m-%d', labelAngle=-45)),  # Tilt x-axis labels
    y=alt.Y('active_users:Q', title='Active Users', axis=alt.Axis(titleColor='black')),
    tooltip=[
        alt.Tooltip('created_at:T', title='Registered Date', format='%Y-%m-%d'), 
        alt.Tooltip('active_users:Q', title='Active Users')
    ]
).properties(
    width=600,
    height=400
)

# Display the chart
st.altair_chart(line_chart, use_container_width=True)


# Breakdown data table for active users
with st.expander("View Active Users Breakdown"):
    st.dataframe(active_user_counts)

# Platform Distribution
st.subheader('Platform Distribution', divider='gray')

# Create a bar chart breakdown by platform and learner_status
platform_breakdown = (filtered_df
                      .groupby(['platform', 'learner_status'])
                      .agg(active_users=('email', 'nunique'))
                      .reset_index())

# Generate the stacked bar chart using Altair
bar_chart = alt.Chart(platform_breakdown).mark_bar().encode(
    x=alt.X('platform:O', title='Platform'),
    y=alt.Y('active_users:Q', title='Active Users'),
    color=alt.Color('learner_status:N', title='Learner Status', scale=alt.Scale(domain=['Active', 'Passive'], range=['#0056b3', '#87CEEB'])),
    tooltip=[
        alt.Tooltip('platform:O', title='Platform'),
        alt.Tooltip('learner_status:N', title='Learner Status'),
        alt.Tooltip('active_users:Q', title='Active Users')
    ]
).properties(
    width=600,
    height=400
)

# Add a text layer to display active user counts within each color section
text_active = bar_chart.mark_text(
    align='center',
    baseline='middle',
    fontSize=14,
    dy=2,  # Positioning text slightly inside the active (blue) bar
    fontWeight='bold'
).transform_filter(
    alt.datum.learner_status == 'Active'
).encode(
    text=alt.Text('active_users:Q'),
    color=alt.value('black')  # White text for better contrast on the dark blue bar
)

text_passive = bar_chart.mark_text(
    align='center',
    baseline='middle',
    fontSize=14,
    dy=5,  # Positioning text slightly inside the passive (light blue) bar
    fontWeight='bold'
).transform_filter(
    alt.datum.learner_status == 'Passive'
).encode(
    text=alt.Text('active_users:Q'),
    color=alt.value('black')  # Black text for better contrast on the light blue bar
)

# Layer the bar chart with the text labels for both active and passive users
layered_chart = bar_chart + text_active + text_passive

# Display the bar chart in Streamlit
st.altair_chart(layered_chart, use_container_width=True)

# Breakdown data table for active users
with st.expander("View Learners Breakdown"):
    st.dataframe(platform_breakdown)
