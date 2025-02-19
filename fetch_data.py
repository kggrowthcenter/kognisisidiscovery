import streamlit as st
import pandas as pd
import pymysql
from sshtunnel import SSHTunnelForwarder
import paramiko
from io import StringIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import toml


# Function to connect to Discovery and fetch data for the main query
@st.cache_resource
def fetch_data_discovery():
    return fetch_data_from_query('query_discovery.sql')


# Function to connect to Discovery and fetch data for Active Learners
@st.cache_resource
def fetch_data_discovery_al():
    return fetch_data_from_query('query_DiscoveryAL.sql')


# Function to connect to Discovery and fetch data for Active Users
@st.cache_resource
def fetch_data_discovery_au():
    return fetch_data_from_query('query_DiscoveryAU.sql')


# Helper function to fetch data based on SQL file
def fetch_data_from_query(query_file):
    try:
        connection_kwargs = {
            'host': st.secrets["discovery"]["host"],
            'port': st.secrets["discovery"]["port"],
            'user': st.secrets["discovery"]["user"],
            'password': st.secrets["discovery"]["password"],
            'database': st.secrets["discovery"]["database"],
            'cursorclass': pymysql.cursors.DictCursor,
        }
        conn = pymysql.connect(**connection_kwargs)

        with open(query_file, 'r') as sql_file:
            query = sql_file.read()

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"An error occurred while fetching data from {query_file}: {e}")
        return pd.DataFrame()


@st.cache_resource
def fetch_data_capture():
    secret_info = st.secrets["json_sap"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open('0. Data Capture - Monthly Updated')
    
    # Ambil data dari sheet1, sheet2, dan sheet3
    sheet1 = spreadsheet.get_worksheet(0)
    sheet2 = spreadsheet.get_worksheet(1)
    sheet3 = spreadsheet.get_worksheet(2)
   
    data1 = sheet1.get_all_records()
    data2 = sheet2.get_all_records()
    data3 = sheet3.get_all_records()
    
    df_capture_sheet1 = pd.DataFrame(data1)
    df_capture_sheet2 = pd.DataFrame(data2)
    df_capture_sheet3 = pd.DataFrame(data3)
    
    return df_capture_sheet1, df_capture_sheet2, df_capture_sheet3


# Function to fetch data from SAP with selected columns
@st.cache_resource
def fetch_data_sap(selected_columns):
    secret_info = st.secrets["json_sap"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open('0. Active Employee - Monthly Updated')
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df[selected_columns]
