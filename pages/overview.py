import streamlit as st
from components.data_loader import load_data
import pandas as pd

# @st.cache()
def app():
    # Title and description
    st.title("Dashboard")
    st.write("This is the Dashboard page.")

    # Load data
    df = load_data('Oct_2019.pkl')

    # Data preprocessing
    if not df.empty:
        startDate = df['event_time'].min()
        endDate = df['event_time'].max()

        # Date range selection
        with st.sidebar:
            st.subheader("Date Range Selection")
            date1 = pd.to_datetime(st.date_input('Start Date', startDate))
            date2 = pd.to_datetime(st.date_input('End Date', endDate))

        # Filter data by date range
        df = df[(df['event_time'] >= date1) & (df['event_time'] <= date2)].copy()

        # Display filtered data
        st.subheader("Filtered Data")
        st.write(df.head())  # Display a preview of the filtered data
    else:
        st.warning("No data available. Please check the input file.")

# Run the app
if __name__ == "__main__":
    app()
