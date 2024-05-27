# import os
# import streamlit as st
# import dask.dataframe as dd
# import pandas as pd
# import datetime


# # @st.cache()
# def app():
#     # Title and description
#     st.title("Dashboard")
#     st.write("This is the Dashboard page.")

#     path = os.path.join('data', 'daily_summary_table.csv')
#     # Load data
#     try:
#         df = pd.read_csv(path, encoding='UTF-8-SIG')
#         df['event_time'] = pd.to_datetime(df['event_time'], format='%Y-%m-%d')
#     #     df['event_time'] = [datetime.datetime.strptime(
#     #         str(target_date).split(" ")[0], '%Y-%m-%d').date()
#     #     for target_date in df["event_time"]
#     # ]
#         # st.write(df.head()) 
#         st.write(df['event_time'].min().strftime('%Y-%m-%d'))
        
#     except Exception as e:
#         st.error(f"Error loading data: {e}")
        
    

# # #     # Data preprocessing
#     if not df.empty:
#         startDate = df['event_time'].min()
#         endDate = df['event_time'].max()

#         col1, col2 = st.columns((2))

#         # Date range selection
#         # with st.sidebar:
#         #     st.subheader("Date Range Selection")
#         with col1:
#             date1 = pd.to_datetime(st.date_input('Start Date', startDate))

#         with col2:
#             date2 = pd.to_datetime(st.date_input('End Date', endDate))

#     if date1 == date2:
#         # Filter for a single day
#         df_filtered = df[df['event_time'] == date1 + pd.Timedelta(days=1)].copy()
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

# if __name__ == "__main__":
#     app()

################################################################################################


import os
import streamlit as st
import pandas as pd
from components import charts 

def app():
    # Title and description
    st.title("Dashboard")
    st.write("This is the Dashboard page.")

    path = os.path.join('data', 'daily_summary_table.csv')
    # Load data
    try:
        df = pd.read_csv(path, encoding='UTF-8-SIG')
        df['event_time'] = pd.to_datetime(df['event_time'], format='%Y-%m-%d')
        st.write(df['event_time'].min().strftime('%Y-%m-%d'))
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        
    # Data preprocessing
    if not df.empty:
        startDate = df['event_time'].min()
        endDate = df['event_time'].max()

        col1, col2 = st.columns(2)

        # Date range selection
        with col1:
            date1 = st.date_input('Start Date', startDate)

        with col2:
            date2 = st.date_input('End Date', endDate)

        date1_timestamp = pd.Timestamp(date1)
        date2_timestamp = pd.Timestamp(date2)

        if date1_timestamp == date2_timestamp:
            # Filter for a single day
            df_filtered = df[df['event_time'].dt.date == date1_timestamp.date()].copy()
        elif date1_timestamp != date2_timestamp:
            # Filter for a date range
            df_filtered = df[(df['event_time'] >= date1_timestamp) & (df['event_time'] <= date2_timestamp)].copy()       


        df_filtered['event_time'] = df_filtered['event_time'].dt.strftime('%Y-%m-%d')
        # Display filtered data
        df_filtered.drop(columns=['conversion_rate'] , inplace=True)
        monthly_summary_table = (
            df.groupby(df['event_time'].dt.to_period('M'))
            .agg(
                Number_of_daily_visits=('Number_of_daily_visits', 'sum'),
                Number_of_daily_visitors=('Number_of_daily_visitors', 'sum'),
                Number_of_purchase_sessions=('Number_of_purchase_sessions', 'sum'),
                Number_of_view_sessions=('Number_of_view_sessions', 'sum'),
                Number_of_cart_sessions=('Number_of_cart_sessions', 'sum'),
                Total_sessions=('Total_sessions', 'sum')
            )
            .reset_index()
            .assign(
                conversion_rate=lambda x: x['Number_of_purchase_sessions'] / x['Number_of_daily_visits']
            )
        )
        category_order = ['Total Sessions', 'View', 'Cart', 'Purchase']

        # Melt the data for plotting
        funnel_data = pd.melt(monthly_summary_table, 
                            id_vars=['event_time'], 
                            value_vars=['Total_sessions', 'Number_of_view_sessions', 'Number_of_cart_sessions', 'Number_of_purchase_sessions'],
                            var_name='Event Type', 
                            value_name='Number of Sessions')

        # Correct event type mapping
        event_type_mapping = {
            'Total_sessions': 'Total Sessions',
            'Number_of_view_sessions': 'View',
            'Number_of_cart_sessions': 'Cart',
            'Number_of_purchase_sessions': 'Purchase'
        }
        funnel_data['Event Type'] = funnel_data['Event Type'].map(event_type_mapping)

        # Reorder the funnel_data DataFrame
        funnel_data['Event Type'] = pd.Categorical(funnel_data['Event Type'], categories=category_order, ordered=True)
        funnel_data = funnel_data.sort_values('Event Type')
        col3 , col4 = st.columns((2))

        with col3:
            fig1 = charts.create_funnel_plot(funnel_data, x_col= 'Number of Sessions', y_col='Event Type', height=500, title='Over All Funnel')
            st.plotly_chart(fig1, use_container_width=True)

        with col4:
            st.subheader("Filtered Data")
            st.dataframe(data=df_filtered, use_container_width=True, hide_index=True)  # Display a preview of the filtered data

    else:
        st.warning("No data available. Please check the input file.")    

if __name__ == "__main__":
    app()

