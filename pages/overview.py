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
import plotly.graph_objects as go
import math
from plotly.subplots import make_subplots
import plotly.express as px

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

        # styled_df = df_filtered.style.highlight_min(color='lightgreen').highlight_max(color='lightcoral')

        df_for_mean = df_filtered.copy(deep=True)

                # Specify the subset of columns to highlight min and max values
        # Display filtered data
        # df_filtered['event_time'] = pd.to_datetime(df_filtered['event_time'])
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
        df_filtered['event_time'] = pd.to_datetime(df_filtered['event_time'])
        daily_summary_table = (
            df.groupby(df_filtered['event_time'].dt.day_name())
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
        mean_conversion_rate = df_for_mean['conversion_rate'].mean()
        fig_mean = charts.create_line_plot_with_mean(data=df_for_mean, x_col='event_time', y_col='conversion_rate', mean_y=mean_conversion_rate, mean_line_dash='dash', mean_line_position='top left')
        st.plotly_chart(fig_mean, use_container_width=True)
        st.divider()

        col3 , col4 = st.columns((2))
        with col3:
            fig1 = charts.create_funnel_plot(funnel_data, x_col= 'Number of Sessions', y_col='Event Type', height=500, title='Over All Funnel')
            st.plotly_chart(fig1, use_container_width=True)

        with col4:
            st.subheader("Filtered Data")
            columns_to_style = df_filtered.columns.difference(['event_time'])

        # Highlight min and max values
            styled_df = df_filtered.style.highlight_min(subset=columns_to_style, color='lightcoral') \
                                     .highlight_max(subset=columns_to_style, color='lightgreen')
            st.dataframe(data=styled_df , use_container_width=True, hide_index=True)  # Display a preview of the filtered data

        st.divider()
        

        # Melt the daily_summary_table
        daily_funnel_data = pd.melt(daily_summary_table, 
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

        daily_funnel_data['Event Type'] = daily_funnel_data['Event Type'].map(event_type_mapping)
        # Define custom order for day names
        custom_day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Calculate the number of rows and columns dynamically based on the number of unique day names
        # num_days = len(custom_day_order)
        # num_rows = math.ceil(num_days / 4)
        # num_cols = min(num_days, 4)
        # # Create subplots with dynamic rows and columns
        # fig_funnel = make_subplots(
        #     rows=num_rows, 
        #     cols=num_cols,
        #     subplot_titles=custom_day_order,
        #     horizontal_spacing=0.15,
        #     vertical_spacing=0.2,
        #     specs=[[{"type": "funnel"}]*num_cols]*num_rows
        #         )       
        
        # # Iterate over each day and add the corresponding funnel plot
        # for i, day in enumerate(custom_day_order, start=1):
        #     day_data = daily_funnel_data[daily_funnel_data['event_time'] == day]
        #     row = math.ceil(i / num_cols)
        #     col = i if num_cols == 1 else (i + 1) % num_cols + 1

        #     fig_funnel.add_trace(
        #         go.Funnel(
        #             x=day_data['Number of Sessions'],
        #             y=day_data['Event Type'],
        #             name=day,
        #             textinfo="value+percent previous",
        #             marker=dict(opacity=0.7)
        #         ),
        #         row=row, col=col
        #     )

        # # Update layout
        # fig_funnel.update_layout(
        #     title='Funnel Analysis by Day',
        #     showlegend=False,
        #     height=800,  # Adjust the height of the whole figure
        #     width=1200,  # Adjust the width of the whole figure
        #     margin=dict(l=50, r=50, t=100, b=50),  # Adjust the margin
        #     title_x=0.5,  # Set the title's x position to the center
        #     title_y=0.95 
        # )

        # # Hide y-axis tick labels for columns 2 onwards in all rows
        # for row in range(1, num_rows + 1):
        #     for col in range(2, num_cols + 1):
        #         fig_funnel.update_yaxes(showticklabels=False, row=row, col=col)

        
        # # Hide subplots for days not present in the data
        # for i in range(len(custom_day_order), num_rows * num_cols):
        #     row = math.ceil(i / num_cols)
        #     col = i if num_cols == 1 else (i - 1) % num_cols + 1
        #     fig_funnel.update_traces(visible=False, row=row, col=col)

        # Filter the data for the required event types
        daily_funnel_data = daily_funnel_data[daily_funnel_data['Event Type'].isin(['Purchase', 'Cart'])]

        # Pivot the data to create a table with event_time as the index and event types as columns
        pivot_df = pd.pivot_table(daily_funnel_data, index='event_time', columns='Event Type', values='Number of Sessions')

        # Reset the index to turn the index back into a column
        pivot_df = pivot_df.reset_index()

        # Melt the dataframe to have 'event_time', 'Event Type', and 'Number of Sessions' as columns
        melted_df = pivot_df.melt(id_vars='event_time', var_name='Event Type', value_name='Number of Sessions')

        # Convert event_time to datetime with specified format
        # melted_df['event_time'] = pd.to_datetime(melted_df['event_time'], format='%Y-%m-%d')

        # Extract day names from the event_time
        # melted_df['day_name'] = melted_df['event_time'].dt.day_name()

        # Define the custom order for the days of the week
        custom_day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Ensure the day_name column follows the custom order
        melted_df['event_time'] = pd.Categorical(melted_df['event_time'], categories=custom_day_order, ordered=True)

        # Plot the bar chart with Plotly Express
        fig = px.bar(
            melted_df,
            x='event_time',
            y='Number of Sessions',
            color='Event Type',
            barmode='group',
            title='Number of Sessions by Event Type Over Time',
            category_orders={'event_time': custom_day_order}  # Use the correct key for category_orders
        )

        # Update the layout of the plot
        fig.update_layout(
            xaxis_title='Event Time',
            yaxis_title='Number of Sessions',
            legend_title='Event Type'
        )

        # Display the plot using Streamlit
        st.plotly_chart(fig)

        daily_funnel_data = daily_funnel_data.sort_values('Event Type')
        st.write(daily_funnel_data)

        # Display the figure using st.plotly_chart
        # st.plotly_chart(fig_funnel)


    else:
        st.warning("No data available. Please check the input file.")    

if __name__ == "__main__":
    app()

