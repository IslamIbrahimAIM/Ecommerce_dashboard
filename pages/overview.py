import os
import streamlit as st
import pandas as pd
from components import charts 
import plotly.graph_objects as go
import math
from plotly.subplots import make_subplots
import plotly.express as px
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Path to the data file
path = os.path.join('data', 'daily_summary_table.csv')

# Load data
try:
    df = pd.read_csv(path, encoding='UTF-8-SIG')
    df['event_time'] = pd.to_datetime(df['event_time'], format='%Y-%m-%d')
except Exception as e:
    st.error(f"Error loading data: {e}")

startDate = df['event_time'].min()
endDate = df['event_time'].max()

# Copy the dataframe for Streamlit processing
st_df = df.copy(deep=True)
st_df['conversion_rate'] = (st_df['conversion_rate'] * 100).round(3).astype(str) + '%'

columns_to_style = st_df.columns.difference(['event_time'])

# Highlight min and max values
styled_df = st_df.style.highlight_min(subset=columns_to_style, color='lightcoral') \
                            .highlight_max(subset=columns_to_style, color='lightgreen')

# Copy the dataframe for monthly tables and drop unnecessary columns
monthly_df = df.copy(deep=True)
monthly_df.drop(columns=['conversion_rate'], inplace=True)


@st.cache_data()
# Function to generate funnel data based on the selected grouping period
def get_funnel_data(df, start_date, end_date, period='D'):
    df = df[(df['event_time'] >= start_date) & (df['event_time'] <= end_date)]
    grouped_df = df.groupby(df['event_time'].dt.to_period(period)).agg(
        Number_of_daily_visits=('Number_of_daily_visits', 'sum'),
        Number_of_daily_visitors=('Number_of_daily_visitors', 'sum'),
        Number_of_purchase_sessions=('Number_of_purchase_sessions', 'sum'),
        Number_of_view_sessions=('Number_of_view_sessions', 'sum'),
        Number_of_cart_sessions=('Number_of_cart_sessions', 'sum'),
        Total_sessions=('Total_sessions', 'sum')
    ).reset_index().assign(
        conversion_rate=lambda x: x['Number_of_purchase_sessions'] / x['Number_of_daily_visits']
    )
    
    funnel_data = pd.melt(grouped_df, 
                          id_vars=['event_time'], 
                          value_vars=['Total_sessions', 'Number_of_view_sessions', 'Number_of_cart_sessions', 'Number_of_purchase_sessions', 'conversion_rate'],
                          var_name='Event Type', 
                          value_name='Number of Sessions')
    
    event_type_mapping = {
        'Total_sessions': 'Total Sessions',
        'Number_of_view_sessions': 'View',
        'Number_of_cart_sessions': 'Cart',
        'Number_of_purchase_sessions': 'Purchase',
        'conversion_rate': 'Conversion Rate'
    }
    funnel_data['Event Type'] = funnel_data['Event Type'].map(event_type_mapping)
    
    return funnel_data

def get_data_by_day_name(df, start_date, end_date):
    df = df[(df['event_time'] >= start_date) & (df['event_time'] <= end_date)]
    grouped_df = df.groupby(df['event_time'].dt.day_name()).agg(
    Number_of_daily_visits=('Number_of_daily_visits', 'sum'),
    Number_of_daily_visitors=('Number_of_daily_visitors', 'sum'),
    Number_of_purchase_sessions=('Number_of_purchase_sessions', 'sum'),
    Number_of_view_sessions=('Number_of_view_sessions', 'sum'),
    Number_of_cart_sessions=('Number_of_cart_sessions', 'sum'),
    Total_sessions=('Total_sessions', 'sum')
    ).reset_index().assign(
        conversion_rate=lambda x: x['Number_of_purchase_sessions'] / x['Number_of_daily_visits']
    )
    
    day_name_data = pd.melt(grouped_df, 
                          id_vars=['event_time'], 
                          value_vars=['Total_sessions', 'Number_of_view_sessions', 'Number_of_cart_sessions', 'Number_of_purchase_sessions', 'conversion_rate'],
                          var_name='Event Type', 
                          value_name='Number of Sessions')
    
    event_type_mapping = {
        'Total_sessions': 'Total Sessions',
        'Number_of_view_sessions': 'View',
        'Number_of_cart_sessions': 'Cart',
        'Number_of_purchase_sessions': 'Purchase',
        'conversion_rate': 'Conversion Rate'
    }
    day_name_data['Event Type'] = day_name_data['Event Type'].map(event_type_mapping)

    return day_name_data


# Main app function
def app():
    # Title and description
    st.title("Dashboard")
    st.write("This is the Testing page.")

    col1, col2 = st.columns(2)
    
    # Date range selection
    with col1:
        date1 = st.date_input('Start Date', startDate)
        
    with col2:
        date2 = st.date_input('End Date', endDate)

    date1_timestamp = pd.Timestamp(date1)
    date2_timestamp = pd.Timestamp(date2)


    st.divider()


    # Calculate the number of days between the selected dates
    num_days = (date2_timestamp - date1_timestamp).days
    
    # Determine the grouping period based on the number of days
    if num_days < 6:
        period = 'D'  # Daily for up to 1 week
    elif num_days < 30:
        period = 'W'  # Weekly for up to 1 month
    else:
        period = 'M'  # Monthly for more than 1 month

    if date1_timestamp == date2_timestamp:
        # Filter for a single day
        filtered_df = st_df[st_df['event_time'].dt.date == date1_timestamp.date()].copy()
    else:
        # Filter for a date range
        filtered_df = st_df[(st_df['event_time'] >= date1_timestamp) & (st_df['event_time'] <= date2_timestamp)].copy()

    # Apply highlighting to the filtered dataframe
    filtered_df["event_time"] = [
        datetime.datetime.strptime(str(target_date).split(" ")[0], '%Y-%m-%d').date()
        for target_date in filtered_df["event_time"]
    ]

    mean_df = filtered_df.drop(columns='conversion_rate').copy(deep=True)
    mean_df['conversion_rate'] = mean_df['Number_of_purchase_sessions'] / mean_df['Number_of_daily_visits']

    styled_df = filtered_df.style.highlight_min(subset=columns_to_style, color='#E6A8BF') \
                                 .highlight_max(subset=columns_to_style, color='#A8E6CF')
    


    # Define the previous period
    if period == 'D':
        previous_period_start = date1_timestamp - pd.DateOffset(days=num_days + 1)
        previous_period_end = date1_timestamp - pd.DateOffset(days=1)
    elif period == 'W':
        previous_period_start = date1_timestamp - pd.DateOffset(weeks=num_days // 7 + 1)
        previous_period_end = date1_timestamp - pd.DateOffset(days=1)
    elif period == 'M':
        previous_period_start = date1_timestamp - pd.DateOffset(months=num_days // 30 + 1)
        previous_period_end = date1_timestamp - pd.DateOffset(days=1)

    # Filter data for current and previous periods
    
    previous_data = df[(df['event_time'] >= previous_period_start) & (df['event_time'] <= previous_period_end)]

    # Generate funnel data
    previous_funnel_data = get_funnel_data(previous_data, previous_period_start, previous_period_end, period)

    # Generate funnel data
    funnel_data = get_funnel_data(df, date1_timestamp, date2_timestamp, period)
    
    # Layout for the plots and dataframes
    if num_days >= 30:
        funnel_col, df_col = st.columns((2))
    else:
        funnel_col, df_col, extra_col = st.columns((3))
    
    # Display funnel plot or bar chart based on the period
    with funnel_col:
        if period == 'M':
            full_funnel = funnel_data[funnel_data['Event Type'] != 'conversion_rate'].copy()
            fig1 = charts.create_funnel_plot(data=full_funnel, x_col='Number of Sessions', y_col='Event Type', height=500, title='Overall Funnel')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            bar_funnel = funnel_data[funnel_data['Event Type'].isin(['Cart', 'Purchase'])].copy()
            previous_bar_funnel = previous_funnel_data[previous_funnel_data['Event Type'].isin(['Cart', 'Purchase'])].copy()
            bar_funnel['event_time'] = bar_funnel['event_time'].astype(str)
            fig_bar = px.bar(
                bar_funnel,
                x='event_time',
                y='Number of Sessions',
                color='Event Type',
                barmode='group',
                title='Cart vs Purchase Over Time',
                width=400,
                height=500
            )

            # Update the layout of the plot
            fig_bar.update_layout(
                xaxis_title='Event Time',
                yaxis_title='Sessions Count',
                legend_title='Event Type'
            )

            fig_bar.update_traces(texttemplate='%{y:.2s}', textposition='outside')
            st.plotly_chart(fig_bar)

            # Calculate statistics
            stats = bar_funnel.groupby('Event Type')['Number of Sessions'].agg(['min', 'mean', 'max']).reset_index()
            previous_stats = previous_bar_funnel.groupby('Event Type')['Number of Sessions'].agg(['min', 'mean', 'max']).reset_index()

            # Construct the main line string with mean values
            mean_str = " and ".join([f"{row['Event Type']}: {row['mean']:,.0f}" for index, row in stats.iterrows()])

            if previous_stats.empty:
                previous_mean_str = ''
            else:
                previous_mean_str = " and ".join([f" {row['Event Type']}: {'Growth' if (row_stats['mean'] - row['mean']) >= 0 else 'Drop'} {(row_stats['mean'] - row['mean']) / row_stats['mean'] * 100:.2f}%" for _, row_stats in stats.iterrows() for _, row in previous_stats.iterrows() if row['Event Type'] == row_stats['Event Type']])

            # Display statistics in the expander
            with st.expander("**Statistics Explanation**"):
                st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                        f"<em>This figure represents Cart and Purchase over time, where the average Sessions for the period is <strong>{mean_str}</strong></em> <b>{previous_mean_str if previous_mean_str else 'No previous data'}</b></div>",
                        unsafe_allow_html=True)
                st.write("---")
                for index, row in stats.iterrows():
                    event_type = row['Event Type']
                    min_value = row['min']
                    mean_value = row['mean']
                    max_value = row['max']

                    min_date = bar_funnel[(bar_funnel['Event Type'] == event_type) & (bar_funnel['Number of Sessions'] == min_value)]['event_time'].values[0]
                    max_date = bar_funnel[(bar_funnel['Event Type'] == event_type) & (bar_funnel['Number of Sessions'] == max_value)]['event_time'].values[0]

                    # Render the content with the custom style
                    st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                                f"<b>{event_type}</b><br>"
                                f"<b>Min:</b> {min_value:,.0f} on <b>{min_date}</b><br>"
                                f"<b>Max:</b> {max_value:,.0f} on <b>{max_date}</b>"
                                "</div>", unsafe_allow_html=True)
    if num_days < 30:
        with extra_col:
            previous_bar_funnel = previous_funnel_data[previous_funnel_data['Event Type'].isin(['Total Sessions', 'View'])].copy()
            bar_funnel = funnel_data[funnel_data['Event Type'].isin(['Total Sessions', 'View'])].copy()
            bar_funnel['event_time'] = bar_funnel['event_time'].astype(str)
            fig_vbar = px.bar(
                bar_funnel,
                x='Number of Sessions', # 'event_time'
                y='event_time', #'Number of Sessions'
                color='Event Type',
                barmode='group',
                title='Total Sessions VS Views Over Time',
                orientation='h',
                width=700,
                height=500,
                color_discrete_sequence= ['#C9C9FF', '#787899', '#9467bd']

            )

            # Update the layout of the plot
            fig_vbar.update_layout(
                xaxis_title='Sessions Count', #Event Time
                yaxis_title='Event Time',
                legend_title='Event Type'
            )

            fig_vbar.update_traces(texttemplate='%{x:.2s}', textposition='outside')
            st.plotly_chart(fig_vbar, use_container_width=True)


            # Calculate statistics
            stats = bar_funnel.groupby('Event Type')['Number of Sessions'].agg(['min', 'mean', 'max']).reset_index()
            previous_stats = previous_bar_funnel.groupby('Event Type')['Number of Sessions'].agg(['min', 'mean', 'max']).reset_index()
            # Construct the main line string with mean values
            mean_str = " and ".join([f"{row['Event Type']}: {row['mean']:,.0f}" for index, row in stats.iterrows()])

            if previous_stats.empty:
                previous_mean_str = ''
            else:
                previous_mean_str = " and ".join([f" {row['Event Type']}: {'Growth' if (row_stats['mean'] - row['mean']) >= 0 else 'Drop'} {(row_stats['mean'] - row['mean']) / row_stats['mean'] * 100:.2f}%" for _, row_stats in stats.iterrows() for _, row in previous_stats.iterrows() if row['Event Type'] == row_stats['Event Type']])            

            # Display statistics in the expander
            with st.expander("**Statistics Explanation**"):
                # st.write(f"*This figure represents Sessions and Views over time, where the average Sessions for the period is **{mean_str}***")
                st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                        f"<em>This figure represents Total Sessions and Views over time, where the average Sessions for the period is <strong>{mean_str}</strong></em> <b>{previous_mean_str if previous_mean_str else 'No previous data' }</b></div>",
                        unsafe_allow_html=True)
                st.write("---")
                for index, row in stats.iterrows():
                    event_type = row['Event Type']
                    min_value = row['min']
                    mean_value = row['mean']
                    max_value = row['max']

                    min_date = bar_funnel[(bar_funnel['Event Type'] == event_type) & (bar_funnel['Number of Sessions'] == min_value)]['event_time'].values[0]
                    max_date = bar_funnel[(bar_funnel['Event Type'] == event_type) & (bar_funnel['Number of Sessions'] == max_value)]['event_time'].values[0]

                    st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                                f"<b>{event_type}</b><br>"
                                f"<b>Min:</b> {min_value:,.0f} on <b>{min_date}</b><br>"
                                f"<b>Max:</b> {max_value:,.0f} on <b>{max_date}</b>"
                                "</div>", unsafe_allow_html=True)
                    

        with df_col:
            previous_mean_df = previous_data.drop(columns='conversion_rate').copy(deep=True)
            previous_mean_df['conversion_rate'] = previous_mean_df['Number_of_purchase_sessions'] / previous_mean_df['Number_of_daily_visits']
            mean_conversion_rate = mean_df['conversion_rate'].mean()
            previous_mean_conversion_rate = previous_mean_df['conversion_rate'].mean()
            fig_mean = charts.create_line_plot_with_mean(data=mean_df, x_col='event_time', y_col='conversion_rate', mean_y=mean_conversion_rate, mean_line_dash='dash', mean_line_position='top left', width=400, height=500, title='Conversion Rate Line Plot')
            # Calculate growth
            growth_percentage = (mean_conversion_rate - previous_mean_conversion_rate) / previous_mean_conversion_rate * 100
            growth_status = "Growth" if growth_percentage > 0 else "Drop"
            st.plotly_chart(fig_mean)

            with st.expander("**Statistics Explanation**"):
                st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'><em>This figure is representing the trend of conversion rate over time along with the average conversion rate of </em><b>{mean_conversion_rate * 100:.3f}%</b> <em>in the selected period while average conversion rate of previous period is </em><b>{previous_mean_conversion_rate * 100:.3f}% </b><em>and the trend shows a </em><b>{growth_status}</b> of <b>{abs(growth_percentage):.2f}%</b>", unsafe_allow_html=True)


                st.write("---")
                min_conversion_rate = mean_df['conversion_rate'].min()
                max_conversion_rate = mean_df['conversion_rate'].max()
                min_date = mean_df[mean_df['conversion_rate'] == min_conversion_rate]['event_time'].values[0]
                max_date = mean_df[mean_df['conversion_rate'] == max_conversion_rate]['event_time'].values[0]
                st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                            f"<b>Conversion Rate:</b><br>"
                            f"<b>Min Value:</b> {min_conversion_rate * 100:.3f}% on <b>{min_date}</b><br>"
                            f"<b>Max Value:</b> {max_conversion_rate * 100:.3f}% on <b>{max_date}</b>",
                            unsafe_allow_html=True
                            )

        
    else:
        with df_col:
            # Dictionary to map original column names to custom column names
            columns_to_rename = {
                'event_time': 'Date',
                'Total_sessions': 'Total Sessions',
                'Number_of_cart_sessions': 'Cart Sessions',
                'Number_of_purchase_sessions': 'Orders'
            }
            # Add thousand separators to 'Total_sessions'
            # Format numeric columns except 'event_time' and 'Conversion_rate'
            numeric_cols = [col for col in styled_df.data.columns if col in ['Total_sessions', 'Number_of_cart_sessions', 'Number_of_purchase_sessions']]
            for col in numeric_cols:
                styled_df.data[col] = styled_df.data[col].map('{:,.0f}'.format)
            st.dataframe(data=styled_df, use_container_width=True, hide_index=True, column_order=list(columns_to_rename.keys()),column_config={
                'event_time': 'Date',
                'Total_sessions': st.column_config.NumberColumn(
                    'Total Sessions',
                    format= '{%.0f}'   
                ),
                'Number_of_view_sessions': st.column_config.NumberColumn(
                    'Total Views',
                    format= '{%.0f}'   
                ),
                'Number_of_cart_sessions': st.column_config.NumberColumn(
                    'Total Cart',
                    format= '{%.0f}'   
                ),
                'Number_of_purchase_sessions': st.column_config.NumberColumn(
                    'Total Orders',
                    format= '{%.0f}'   
                ),

            })

    st.divider()
    day_name_data = get_data_by_day_name(df, date1_timestamp, date2_timestamp)
    # Define custom sort order for event_time
    custom_sort_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    day_name_data_sessions = day_name_data[day_name_data['Event Type'] == 'Total Sessions'].copy()
    day_name_data_sessions = day_name_data_sessions.rename(columns={'event_time': 'Day Name', 'Number of Sessions': 'Sessions'})

    # Convert event_time to categorical variable with custom sort order
    day_name_data_sessions['Day Name'] = pd.Categorical(day_name_data_sessions['Day Name'], categories=custom_sort_order, ordered=True)
    # Sort the DataFrame by event_time
    day_name_data_sessions = day_name_data_sessions.sort_values('Day Name')


    day_name_data_view = day_name_data[day_name_data['Event Type'] == 'View'].copy()
    day_name_data_view = day_name_data_view.rename(columns={'event_time': 'Day Name', 'Number of Sessions': 'View'})

    # Convert event_time to categorical variable with custom sort order
    day_name_data_view['Day Name'] = pd.Categorical(day_name_data_view['Day Name'], categories=custom_sort_order, ordered=True)
    # Sort the DataFrame by event_time
    day_name_data_view = day_name_data_view.sort_values('Day Name')


    day_name_data_cart = day_name_data[day_name_data['Event Type'] == 'Cart'].copy()
    day_name_data_cart = day_name_data_cart.rename(columns={'event_time': 'Day Name', 'Number of Sessions': 'Cart'})


    # Convert event_time to categorical variable with custom sort order
    day_name_data_cart['Day Name'] = pd.Categorical(day_name_data_cart['Day Name'], categories=custom_sort_order, ordered=True)
    # Sort the DataFrame by event_time
    day_name_data_cart = day_name_data_cart.sort_values('Day Name')


    day_name_data_purchase = day_name_data[day_name_data['Event Type'] == 'Purchase'].copy()
    day_name_data_purchase = day_name_data_purchase.rename(columns={'event_time': 'Day Name', 'Number of Sessions': 'Orders'})
    
    # Convert event_time to categorical variable with custom sort order
    day_name_data_purchase['Day Name'] = pd.Categorical(day_name_data_purchase['Day Name'], categories=custom_sort_order, ordered=True)
    # Sort the DataFrame by event_time
    day_name_data_purchase = day_name_data_purchase.sort_values('Day Name')

    pie_plot_sessions_col, pie_plot_view_col, pie_plot_cart_col, pie_plot_purchase_col = st.columns((4))

    with pie_plot_sessions_col:
        # Sort the DataFrame by event_time
        day_name_data_sessions = day_name_data_sessions.sort_values('Day Name')

        # Calculate values and labels for the pie chart
        labels = day_name_data_sessions['Day Name']
        values = day_name_data_sessions['Sessions']
        # Define the pastel blue colors
        colors = ['#C9E4FF', '#AED6F1', '#92C2ED', '#7FB3E2', '#6BAFE4', '#5DADE2', '#4A90E2']

        # Create a pie chart using Plotly Graph Objects
        pie_plot_sessions_fig = go.Figure(data=[go.Pie(labels=labels, values=values, sort=False, marker=dict(colors=colors))])
        pie_plot_sessions_fig.update_layout(legend=dict(orientation="h", yanchor="top", y= 1.3, xanchor="center", x=0.5))


        numeric_cols = [col for col in day_name_data_sessions.columns if col in ['Sessions']]
        for col in numeric_cols:
                day_name_data_sessions[col] = day_name_data_sessions[col].map('{:,.0f}'.format)
        with st.container():
            st.markdown("<h5 style='text-align: center;'>Sessions by Day Name</h5>", unsafe_allow_html=True)
            st.plotly_chart(pie_plot_sessions_fig, use_container_width=True)
            st.dataframe(day_name_data_sessions, hide_index=True, column_order=['Day Name', 'Sessions'], use_container_width=True)


    with pie_plot_view_col:
        day_name_data_view = day_name_data_view.sort_values('Day Name')
        labels = day_name_data_view['Day Name']
        values = day_name_data_view['View']

        # Define the pastel blue colors
        colors = ['#DFDFFF', '#EAEAFF', '#F5F5FF', '#D4D4FF', '#BEBEFF', '#B3B3FF', '#A8A8FF']
        pie_plot_view_fig = go.Figure(data=[go.Pie(labels=labels, values=values, sort=False, marker=dict(colors=colors))])
        pie_plot_view_fig.update_layout(legend=dict(orientation="h", yanchor="top", y= 1.3, xanchor="center", x=0.5))


        numeric_cols = [col for col in day_name_data_view.columns if col in ['View']]
        for col in numeric_cols:
                day_name_data_view[col] = day_name_data_view[col].map('{:,.0f}'.format)

        with st.container():
            st.markdown("<h5 style='text-align: center;'>Views by Day Name</h5>", unsafe_allow_html=True)
            st.plotly_chart(pie_plot_view_fig, use_container_width=True)
            st.dataframe(day_name_data_view, hide_index=True, column_order=['Day Name', 'View'], use_container_width=True) 

    with pie_plot_cart_col:
        day_name_data_cart = day_name_data_cart.sort_values('Day Name')
        labels = day_name_data_cart['Day Name']
        values = day_name_data_cart['Cart']
        # Define the pastel blue colors
        colors = ["#FFC590", "#FFCCA8", "#FFD3C0", "#FFDAD8", "#FFB560", "#FFAD48", "#FFA530"]
        pie_plot_cart_fig = go.Figure(data=[go.Pie(labels=labels, values=values, sort=False, marker=dict(colors=colors))])
        pie_plot_cart_fig.update_layout(legend=dict(orientation="h", yanchor="top", y= 1.3, xanchor="center", x=0.5))




        numeric_cols = [col for col in day_name_data_cart.columns if col in ['Cart']]
        for col in numeric_cols:
                day_name_data_cart[col] = day_name_data_cart[col].map('{:,.0f}'.format)        

        with st.container():
            st.markdown("<h5 style='text-align: center;'>Cart by Day Name</h5>", unsafe_allow_html=True)
            st.plotly_chart(pie_plot_cart_fig, use_container_width=True)
            st.dataframe(day_name_data_cart, hide_index=True, column_order=['Day Name', 'Cart'], use_container_width=True)


    with pie_plot_purchase_col:
        day_name_data_purchase = day_name_data_purchase.sort_values('Day Name')
        labels = day_name_data_purchase['Day Name']
        values = day_name_data_purchase['Orders']
        # Define the pastel blue colors
        colors = ["#9BD7DF", "#ACDFE7", "#BDE7EF", "#CEEFF7", "#79C5CF", "#68BDC7", "#57B5BF"]
        pie_plot_purchase_fig = go.Figure(data=[go.Pie(labels=labels, values=values, sort=False, marker=dict(colors=colors), hole=0.5)])
        pie_plot_purchase_fig.update_layout(legend=dict(orientation="h", yanchor="top", y= 1.3, xanchor="center", x=0.5))


        numeric_cols = [col for col in day_name_data_purchase.columns if col in ['Orders']]
        for col in numeric_cols:
                day_name_data_purchase[col] = day_name_data_purchase[col].map('{:,.0f}'.format) 


        with st.container():
            st.markdown("<h5 style='text-align: center;'>Orders by Day Name</h5>", unsafe_allow_html=True)
            st.plotly_chart(pie_plot_purchase_fig, use_container_width=True)
            st.dataframe(day_name_data_purchase, hide_index=True, column_order=['Day Name', 'Orders'], use_container_width=True)

    
    pivot_df = day_name_data.pivot_table(index='event_time', columns='Event Type', values='Number of Sessions', aggfunc='sum')
    pivot_df['Cart%'] = (pivot_df['Cart'] / pivot_df['Total Sessions']) * 100
    pivot_df['CR%'] = (pivot_df['Purchase'] / pivot_df['Total Sessions']) * 100

    # Reset index to prepare for melting
    pivot_df.reset_index(inplace=True)

    # Melt the DataFrame to long format
    melted_df = pivot_df.melt(id_vars='event_time', value_vars=['Cart%', 'CR%'], var_name='Metric', value_name='Percentage')

    # Define pastel colors
    pastel_colors = {
        'Cart%': 'lightblue',
        'CR%': 'lightcoral'
    }
    trend_line_colors = {
        'Cart%': 'cornflowerblue',
        'CR%': 'darkgoldenrod'
    }

    # Create the bar plot using Plotly Express
    fig = px.bar(melted_df, x='event_time', y='Percentage', color='Metric', barmode='group',
                title="Cart Conversion Rate and Conversion Rate Over Time",
                labels={'event_time': 'Day Name', 'Percentage': 'Percentage'},
                color_discrete_map=pastel_colors)

    # Update bar traces to show data on bars
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside', selector=dict(type='bar'))

    # Add trend lines for 'Cart%' and 'CR%'
    for metric in ['Cart%', 'CR%']:
        trend_df = melted_df[melted_df['Metric'] == metric]
        fig.add_trace(go.Scatter(
            x=trend_df['event_time'],
            y=trend_df['Percentage'],
            mode='lines+markers',
            name=f'{metric} Trend',
            line=dict(color=trend_line_colors[metric])
        ))

    fig.update_layout(legend=dict(orientation="h", yanchor="top", x=0.5, xanchor="center", y=1.3), legend_title_text='')
    # Show the plot
    st.plotly_chart(fig, use_container_width=True)

    top_performing_data = get_funnel_data(df, date1_timestamp, date2_timestamp, period='D')
    top_performing_data = top_performing_data[top_performing_data['Event Type']=='Purchase'].sort_values(by='Number of Sessions', ascending=False).copy()
    top_performing_data.drop(columns=['Event Type'], inplace=True)
    top_performing_data_sum = top_performing_data['Number of Sessions'].sum()
    top_performing_data['Cum_perc'] = (top_performing_data['Number of Sessions'].cumsum() / top_performing_data_sum) * 100

    data_70_percent = top_performing_data[top_performing_data['Cum_perc'] <=70].sort_values(by='Cum_perc', ascending=True).copy()
    data_70_percent['Cum_perc'] = data_70_percent['Cum_perc'].round(2).astype(str) + '%'

    data_70_percent.rename(columns={'event_time':'Date', 'Number of Sessions':'Orders', 'Cum_perc': 'Cumilative%'} , inplace=True)
    data_70_percent['Date'] = data_70_percent['Date'].astype(str)
    data_70_percent['Orders'] = data_70_percent['Orders'].astype(int)
    data_70_percent.sort_values(by='Orders', inplace=True)

    st.markdown("<div style='border: 2px solid #0047ab; min-height: 50px; display: block; text-align: center; background: linear-gradient(45deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%);'><h2 style= 'color: white;'> Days the Contributed 70% of orders per period</h2></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    data_70_percent['Date'] = pd.to_datetime(data_70_percent['Date'])
    fig_trend_line = px.scatter(data_70_percent, x='Date', y='Orders', trendline="lowess", title='Orders Trend Over Time')



    # Extract trend line values
    trendline_y = None
    for trace in fig_trend_line.data:
        if trace.mode == 'lines':
            trendline_y = trace.y

    
    # Calculate residuals (difference between actual and trend line)
    residuals = data_70_percent['Orders'] - trendline_y

    # Define "extreme" as points where residuals are more than 2 standard deviations from the mean
    threshold = 2 * np.std(residuals)
    extreme_points = data_70_percent[np.abs(residuals) > threshold]

    # Add scatter plot with highlighted extreme points
    fig_trend_line.add_trace(go.Scatter(
        x=extreme_points['Date'],
        y=extreme_points['Orders'],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Extreme Points'
    ))

    # Update the trend line color to purple
    for trace in fig_trend_line.data:
        if trace.mode == 'lines':
            trace.line.color = '#800080'

    st.plotly_chart(fig_trend_line, use_container_width=True)

    low_performing = top_performing_data[~top_performing_data.index.isin(data_70_percent.index)].copy()

    low_performing['Cum_perc'] = low_performing['Cum_perc'].round(2).astype(str) + '%'

    low_performing.rename(columns={'event_time':'Date', 'Number of Sessions':'Orders', 'Cum_perc': 'Cumilative%'} , inplace=True)
    low_performing['Date'] = low_performing['Date'].astype(str)
    low_performing['Orders'] = low_performing['Orders'].astype(int)
    low_performing.sort_values(by='Orders', inplace=True)
    low_performing['Date'] = pd.to_datetime(low_performing['Date'])

    data_70_percent["Date"] = [
        datetime.datetime.strptime(str(target_date).split(" ")[0], '%Y-%m-%d').date()
        for target_date in data_70_percent["Date"]
    ]

    low_performing["Date"] = [
        datetime.datetime.strptime(str(target_date).split(" ")[0], '%Y-%m-%d').date()
        for target_date in low_performing["Date"]
    ]

    top_order_col, low_order_col = st.columns((2))

    with top_order_col:
        st.markdown("<div style='border: 2px solid #0047ab; min-height: 50px; display: flex; align-items: center; justify-content: center; background: linear-gradient(45deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%);'><h5 style= 'color: white;'>Top Performing Dates</h5></div>", unsafe_allow_html=True)
        st.dataframe(data_70_percent, use_container_width=True, column_order=['Date', 'Orders'], hide_index=True)

    with low_order_col:
        st.markdown("<div style='border: 2px solid #0047ab; min-height: 50px; display: flex; align-items: center; justify-content: center; background: linear-gradient(45deg, rgba(131,58,180,1) 0%, rgba(253,29,29,1) 50%, rgba(252,176,69,1) 100%);'><h5 style= 'color: white;'>Low Performing Dates</h5></div>", unsafe_allow_html=True)
        st.dataframe(low_performing, use_container_width=True, column_order=['Date', 'Orders'], hide_index=True)


    with st.expander("**Top Contributing Dates**"):
        if not extreme_points.empty:
            st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                        f"<p><em>This chart is showing the top dates contributing to <b>70%</b> of the overall orders:</em></p><br>"
                        f"<b>{data_70_percent['Orders'].sum():,.0f} out of {top_performing_data['Number of Sessions'].astype(int).sum():,.0f}</b><br>"
                        f"<p>The following dates represent the extreme values of orders, which will require further investigation by acquiring marketing data promotions online and offline:</p> <b>{' , '.join([date.strftime('%Y-%m-%d') for date in extreme_points['Date']])} and values {' , '.join([format(order, ',') for order in extreme_points['Orders']])}</b>",
                        unsafe_allow_html=True
                        )

        else:
            st.markdown(f"<div style='border: 2px solid #51829B; padding: 10px; margin-bottom: 10px;'>"
                        f"<p><em>This chart is showing the top dates contributing to <b>70%</b> of the overall orders:</em></p><br>"
                        f"<b>{data_70_percent['Orders'].sum():,.0f} out of {top_performing_data['Number of Sessions'].astype(int).sum():,.0f}</b><br>"
                        f"<p>No extreme values of orders were found.</p>",
                        unsafe_allow_html=True
                        )
   
    # fig_trend_bar_low = px.bar(data_70_percent, x='Date', y='Orders')
    # fig_trend_line_low = px.scatter(data_70_percent, x='Date', y='Orders', trendline='lowess', title='Orders Trend Over Time')


    # fig12 = go.Figure(data=fig_trend_bar_low.data + fig_trend_line_low.data)
    # st.plotly_chart(fig12)
    # st.plotly_chart(fig_trend_line_low, use_container_width=True)
    # st.dataframe(data_70_percent)
    # st.dataframe(low_performing)

if __name__ == '__main__':
    app()

