import os
import streamlit as st
import pandas as pd

def app():
    st.title("Sales")
    st.write("This is the Sales page.")
    # Add your sales analysis code here

    path = os.path.join('data', 'daily_summary_table.csv')
    # Load data
    try:
        df = pd.read_csv(path, encoding='UTF-8-SIG')
        df['event_time'] = pd.to_datetime(df['event_time'], format='%Y-%M-%d')
        st.write(df.head()) 
        st.write(df['event_time'].min().strftime('%Y-%m-%d'))
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        
    

# # #     # Data preprocessing
#     if not df.empty:
#         startDate = df['event_time'].min()
#         endDate = df['event_time'].max()

#         # Date range selection
#         with st.sidebar:
#             st.subheader("Date Range Selection")
#             date1 = pd.to_datetime(st.date_input('Start Date', startDate))
#             date2 = pd.to_datetime(st.date_input('End Date', endDate))

#     if date1 == date2:
#         # Filter for a single day
#         df_filtered = df[df['event_time'] >= date1 + pd.Timedelta(days=1)].copy()
#     elif date1 != date2:
#         # Filter for a date range, including the whole end date
#         df_filtered = df[(df['event_time'] >= date1 + pd.Timedelta(days=1)) & (df['event_time'] < date2 + pd.Timedelta(days=2))].copy()       

#         # Filter data by date range
#         # df = df[(df['event_time'] >= date1) & (df['event_time'] <= date2)].copy()

#         # Display filtered data
#         st.subheader("Filtered Data")
#         st.write(df_filtered)  # Display a preview of the filtered data
#     else:
#         st.warning("No data available. Please check the input file.")  



if __name__ == "__main__":
    app()