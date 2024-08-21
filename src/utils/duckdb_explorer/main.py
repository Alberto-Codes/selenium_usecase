# main.py

import time

import altair as alt
import streamlit as st
from data_processing import construct_query, convert_df_to_csv
from db_operations import fetch_columns, fetch_data, fetch_tables, initialize_connection

from config import DB_PATH


@st.cache_resource
def get_connection():
    """Initializes and caches the database connection.

    Returns:
        duckdb.DuckDBPyConnection: A connection object to interact with the
        database.
    """
    return initialize_connection(DB_PATH)


# Initialize connection
con = get_connection()

# Sidebar for table and query selection
st.sidebar.title("Database Explorer")
tables = fetch_tables(con)

# Table selection
selected_table = st.sidebar.selectbox("Select a table to explore", tables)

# Fetch columns from the selected table
columns = fetch_columns(con, selected_table)

# Multiselect for columns
selected_columns = st.sidebar.multiselect(
    "Select columns to display", columns, default=columns
)

# Optional: Add filtering options
where_clause = st.sidebar.text_input("Enter WHERE clause (optional)")

# Construct SQL query
query = construct_query(selected_columns, selected_table, where_clause)

# Execute and display the query with a progress spinner
st.write(f"Executing Query: {query}")
try:
    with st.spinner("Fetching data..."):
        df = fetch_data(con, query)
    st.write(df)
except Exception as e:
    st.error(f"An error occurred: {e}")

# Real-time updates and data summary
if st.sidebar.checkbox("Enable Real-time Updates"):
    refresh_interval = st.sidebar.slider(
        "Refresh interval (seconds)", min_value=1, max_value=60, value=5
    )
    placeholder = st.empty()

    while True:
        df = fetch_data(con, query)
        placeholder.write(df)
        time.sleep(refresh_interval)
        st.experimental_rerun()
else:
    st.write(df)

# Data summary
if st.sidebar.checkbox("Show Summary"):
    st.write(df.describe())

# Conditional alerts based on data
if df.shape[0] > 0 and selected_columns:  # Ensure there's data to check
    if df[selected_columns[0]].max() > 100:
        st.warning(f"Warning: Maximum value in {selected_columns[0]} exceeds 100!")

# Data visualization using Altair
st.sidebar.subheader("Visualize Data")
x_axis = st.sidebar.selectbox("Select X-axis for plot", columns)
y_axis = st.sidebar.selectbox("Select Y-axis for plot", columns)

chart = (
    alt.Chart(df)
    .mark_circle(size=60)
    .encode(x=x_axis, y=y_axis, tooltip=[x_axis, y_axis])
    .interactive()
)

st.altair_chart(chart, use_container_width=True)

# Data export
csv_data = convert_df_to_csv(df)

st.download_button(
    label="Download Data as CSV",
    data=csv_data,
    file_name=f"{selected_table}_data.csv",
    mime="text/csv",
)

# Custom HTML or widgets (Optional)
st.sidebar.subheader("Additional Options")
if st.sidebar.checkbox("Show Custom HTML"):
    st.components.v1.html(
        """
        <div style="text-align: center;">
            <h1>Custom HTML in Streamlit!</h1>
            <button onclick="alert('Hello from Streamlit!')">Click Me</button>
        </div>
        """,
        height=200,
    )
