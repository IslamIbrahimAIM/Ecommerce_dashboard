import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

output_dir = 'data'

sessions_file = os.path.join(output_dir, 'sessions_by_user_cat.pkl')
cart_file = os.path.join(output_dir, 'cart_by_user_cat.pkl')
orders_file = os.path.join(output_dir, 'orders_by_user_cat.pkl')

# Function to load data
st.cache_data
def load_data(file):
    try:
        data = pd.read_pickle(file, compression='gzip')
        return data
    except Exception as e:
        st.error(f"Error loading data from {file}: {e}")
        return pd.DataFrame()

# Load data outside the app function
sessions_data = load_data(sessions_file)
cart_data = load_data(cart_file)
orders_data = load_data(orders_file)
sessions_data['date'] = pd.to_datetime(sessions_data['date'])
cart_data['date'] = pd.to_datetime(cart_data['date'])
orders_data['date'] = pd.to_datetime(orders_data['date'])
startDate = sessions_data['date'].min()
endDate = sessions_data['date'].max()




def group_and_merge_data(sessions_data, cart_data, orders_data, group_columns, merge_columns):
    grouped_sessions = sessions_data.groupby(group_columns, observed=False).agg(
        Sessions=('Sessions', 'sum'),
        Views=('Views', 'sum'),
        # Visitors=('Visitors', 'sum')
    ).reset_index()
    
    grouped_cart = cart_data.groupby(group_columns, observed=False).agg(
        Cart=('Cart', 'sum'),
        Potential_Buyers=('Potential_Buyers', 'sum'),
        Products_in_Cart=('Products_in_Cart', 'sum'),
        Potential_Sales=('Potentianl_sales', 'sum')
    ).reset_index()
    
    grouped_orders = orders_data.groupby(group_columns, observed=False).agg(
        Orders=('Orders', 'sum'),
        Buyers=('Buyers', 'sum'),
        Products_Sold=('Products_Sold', 'sum'),
        Sales=('Sales', 'sum')
    ).reset_index()
    
    merged_data = grouped_sessions.merge(grouped_cart, on=merge_columns, how='outer')
    merged_data = merged_data.merge(grouped_orders, on=merge_columns, how='outer')
    # merged_data['date'] = merged_data['date'].dt.date
    merged_data['date'] = pd.to_datetime(merged_data['date']).dt.date
    # merged_data = merged_data.fillna(0)
    return merged_data

group_columns = ['date', 'user_type', 'category', 'brand']
merge_columns = ['date', 'user_type', 'category', 'brand']

all_data = group_and_merge_data(sessions_data, cart_data, orders_data, group_columns, merge_columns)

@st.cache_data()
def get_funnel_data(df, start_date, end_date, period='D'):
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
    df['date'] = pd.to_datetime(df['date'])
    grouped_df = df.groupby([df['date'].dt.to_period(period), 'user_type'], observed=False).agg(
        Total_Sessions = ('Sessions', 'sum'),
        Total_Views = ('Views', 'sum'),
        Total_Cart = ('Cart', 'sum'),
        Total_Orders = ('Orders', 'sum')
    ).reset_index()

    grouped_df['date'] = grouped_df['date'].dt.to_timestamp().dt.date
    return grouped_df

@st.cache_data()
def get_cat_data_markdown(df, start_date, end_date, period='D'):
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
    df['date'] = pd.to_datetime(df['date'])
    grouped_df = df.groupby([df['date'].dt.to_period(period), 'user_type', 'category'], observed=False).agg(
        Total_Sessions = ('Sessions', 'sum'),
        Total_Views = ('Views', 'sum'),
        Total_Cart = ('Cart', 'sum'),
        Total_Orders = ('Orders', 'sum'),
        Total_Sales = ('Sales', 'sum'),
        Products = ('Products_Sold', 'sum')
    ).reset_index()

    grouped_df['date'] = grouped_df['date'].dt.to_timestamp().dt.date
    return grouped_df

@st.cache_data()
def get_cat_data(df):
    grouped_df = df.groupby(['user_type', 'category'], observed=False).agg(
        Total_Sessions = ('Sessions', 'sum'),
        Total_Views = ('Views', 'sum'),
        Total_Cart = ('Cart', 'sum'),
        Total_Orders = ('Orders', 'sum'),
        Total_Sales = ('Sales', 'sum'),
        Products = ('Products_Sold', 'sum')
    ).reset_index()
    return grouped_df

@st.cache_data()
def get_brand_data(df):
    grouped_df = df.groupby(['user_type', 'brand'], observed=False).agg(
        Sessions = ('Sessions', 'sum'),
        Views = ('Views', 'sum'),
        Cart = ('Cart', 'sum'),
        Orders = ('Orders', 'sum'),
        Sales = ('Sales', 'sum'),
        Products = ('Products_Sold', 'sum'),
        Buyers = ('Buyers', 'sum')
    ).reset_index()
    return grouped_df


class BrandEvaluator:
    def __init__(self, df, views_col, orders_col, sales_col):
        """
        Initialize the BrandEvaluator with a DataFrame and column names.

        Parameters:
            df (pd.DataFrame): The DataFrame containing brands.
            views_col (str): The column name for views.
            orders_col (str): The column name for orders.
            sales_col (str): The column name for sales.
        """
        self.df = df
        self.views_col = views_col
        self.orders_col = orders_col
        self.sales_col = sales_col
        self.quartiles_dict = self.calculate_quartiles()
    
    def calculate_quartiles(self):
        """
        Calculate quartiles for views, orders, and sales.
        """
        views = self.df[self.views_col]
        orders = self.df[self.orders_col]
        sales = self.df[self.sales_col]

        return {
            'views': views.quantile(q=[0.3, 0.6, 0.9]),
            'orders': orders[orders > 0].quantile(q=[0.3, 0.6, 0.9]),
            'sales': sales[sales > 0].quantile(q=[0.3, 0.6, 0.9])
        }

    def classify_metric(self, value, column_name):
        """
        Classify a value based on its column and the pre-calculated quartiles.

        Parameters:
            value: The value to classify.
            column_name: The name of the column to classify.

        Returns:
            int: The classification score.
        """
        thresholds = self.quartiles_dict.get(column_name)
        if thresholds is None:
            return -1

        if value <= thresholds[0.3]:
            return 4
        elif value <= thresholds[0.6]:
            return 3
        elif value <= thresholds[0.9]:
            return 2
        else:
            return 1

    def evaluate_brands(self):
        """
        Evaluate brands and add classification columns to the DataFrame.
        """
        self.df['Views_class'] = self.df[self.views_col].apply(self.classify_metric, args=('views',))
        self.df['Orders_class'] = self.df[self.orders_col].apply(self.classify_metric, args=('orders',))
        self.df['Sales_class'] = self.df[self.sales_col].apply(self.classify_metric, args=('sales',))
        self.df['Score'] = self.df['Views_class'] + self.df['Orders_class'] + self.df['Sales_class']

        def bucket_score(score):
            if score >= 3 and score <=5:
                return "Star"
            elif score >=5 and score <=7:
                return "High Performance"
            elif score >=8 and score <=10:
                return "Low Performance"
            else:
                return "Weak Performance"

        self.df['Score_Bucket'] = self.df['Score'].apply(bucket_score)

        return self.df




def app():
    with st.sidebar:
        st.write('This is Sidebar')
    st.title("Ecom Dashboard")
    # st.write("This is new Version")

    config = {
        'displayModeBar': False,
    }
    
    col1, col2 = st.columns(2)
    
    # Date range selection
    with col1:
        date1 = st.date_input('Start Date', startDate)
        
    with col2:
        date2 = st.date_input('End Date', endDate)

    # Store the selected dates in session state
    st.session_state.selected_dates = (date1, date2)

    # Calculate the number of days between the selected dates
    num_days = (date2 - date1).days
    
    # Determine the grouping period based on the number of days
    if num_days < 7:
        period = 'D'  # Daily for up to 1 week
    elif num_days < 30:
        period = 'W'  # Weekly for up to 1 month
    else:
        period = 'M'  # Monthly for more than 1 month


    # Define the previous period
    if period == 'D':
        previous_period_start = date1 - pd.DateOffset(days=num_days + 1)
        previous_period_end = date1 - pd.DateOffset(days=1)
    elif period == 'W':
        previous_period_start = date1 - pd.DateOffset(weeks=num_days // 7 + 1)
        previous_period_end = date1 - pd.DateOffset(days=1)
    elif period == 'M':
        previous_period_start = date1 - pd.DateOffset(months=num_days // 30 + 1)
        previous_period_end = date1 - pd.DateOffset(days=1)

    def filter_data_by_date(data, date1_timestamp, date2_timestamp):
        # Ensure the 'date' column in data is of type Timestamp
        data['date'] = pd.to_datetime(data['date'])
        
        # Convert date1_timestamp and date2_timestamp to Timestamp if they are not already
        if not isinstance(date1_timestamp, pd.Timestamp):
            date1_timestamp = pd.Timestamp(date1_timestamp)
        if not isinstance(date2_timestamp, pd.Timestamp):
            date2_timestamp = pd.Timestamp(date2_timestamp)
        
        # Filter data based on date range
        if date1_timestamp and date2_timestamp:
            if date1_timestamp == date2_timestamp:
                # Filter for a single day
                filtered_data = data[data['date'] == date1_timestamp].copy()
            else:
                # Filter for a date range
                filtered_data = data[(data['date'] >= date1_timestamp) & (data['date'] <= date2_timestamp)].copy()
        else:
            filtered_data = data.copy()
        
        return filtered_data
    filtered_data = filter_data_by_date(all_data, date1, date2)
    
    # st.dataframe(filtered_data)
    current_funnel = get_funnel_data(filtered_data, date1, date2, period)
    new_user_funnel = current_funnel[current_funnel['user_type'] == 'New_User'].copy()
    returning_user_funnel = current_funnel[current_funnel['user_type'] == 'Returning_User'].copy()

    funnel_col1, funnel_col2, funnel_col3 = st.columns(3)
    new_user_colors = px.colors.qualitative.Pastel1
    returning_user_colors = px.colors.qualitative.Pastel2

    ###### Category Data #####
    category_Data = get_cat_data(filtered_data)     #category_Data category_data_markdown brand_Data class_result cart_df
    category_data_markdown = get_cat_data_markdown(filtered_data, date1, date2, period='D')
    brand_Data = get_brand_data(filtered_data)

    grouped_brand = brand_Data.groupby('brand', observed=False).agg(
        Sessions = ('Sessions', 'sum'),
        Views = ('Views', 'sum'),
        Cart = ('Cart', 'sum'),
        Orders = ('Orders', 'sum'),
        Sales = ('Sales', 'sum'),
        Buyers = ('Buyers', 'sum')
    ).reset_index()

    # class_result = evaluate_brands(grouped_brand, 'Views', 'Orders', 'Sales').copy()
    evaluator = BrandEvaluator(grouped_brand, 'Views', 'Orders', 'Sales')
    class_result = evaluator.evaluate_brands().copy()

    grouped_brand_aban = filtered_data.groupby(['date', 'user_type', 'brand'], observed=False).agg(
        Sessions = ('Sessions', 'sum'),
        Views = ('Views', 'sum'),
        Cart = ('Cart', 'sum'),
        Orders = ('Orders', 'sum'),
        Sales = ('Sales', 'sum'),
        Buyers = ('Buyers', 'sum')
    ).reset_index()

    cart_evaluator = BrandEvaluator(grouped_brand_aban, 'Views', 'Orders', 'Sales')
    cart_df = cart_evaluator.evaluate_brands().copy()
    cart_df['Abandonment Rate'] = cart_df.apply(lambda row: round((row['Cart'] - row['Orders']) / row['Cart'], 2 ) * 100 if row['Cart'] > row['Orders'] else 0, axis=1)

    abndon_df = cart_df[cart_df['Abandonment Rate'] > 0].copy()


    top_performace = filtered_data.groupby('date', observed=False).agg(
        Orders = ('Orders', 'sum'),
        Sales = ('Sales', 'sum')
    ).reset_index()

    top_performace_by_orders = top_performace.sort_values(by='Orders', ascending=False).copy()
    top_performace_by_orders_sum = top_performace_by_orders['Orders'].sum()
    top_performace_by_orders['Cum_perc'] = (top_performace_by_orders['Orders'].cumsum() / top_performace_by_orders_sum) * 100

    data_70_percent = top_performace_by_orders[top_performace_by_orders['Cum_perc'] <=70].sort_values(by='Cum_perc', ascending=True).copy()
    data_70_percent['Cum_perc'] = data_70_percent['Cum_perc'].round(2).astype(str) + '%'

    grouped_top_sales = category_Data.groupby('category', observed=False)['Total_Sales'].sum().reset_index()

    top_performing_cat_without_elec_unk = grouped_top_sales[~grouped_top_sales['category'].isin(['electronics', 'unknown'])].copy().sort_values(by='Total_Sales', ascending=False)
    top_performing_cat_without_elec_unk_sum = top_performing_cat_without_elec_unk['Total_Sales'].sum()
    top_performing_cat_without_elec_unk['Cum_perc'] = (top_performing_cat_without_elec_unk['Total_Sales'].cumsum() / top_performing_cat_without_elec_unk_sum) * 100


    category_data_sessions = category_Data.iloc[:, :3].copy()
    category_data_sessions['Sessions'] = category_Data['Total_Sessions']
    

    #Creating Views plot DF
    category_data_views = category_Data.iloc[:, :3].copy()
    category_data_views['Views'] = category_Data['Total_Views']
    

    #Creating Orders plot DF
    category_data_orders = category_Data.iloc[:, :3].copy()
    category_data_orders['Orders'] = category_Data['Total_Orders']
    

    #Creating Sales plot DF
    category_data_sales = category_Data.iloc[:, :3].copy()
    category_data_sales['Sales'] = category_Data['Total_Sales']


    
    # Function to check if all values in 'number' are zero
    def is_all_zero(funnel_data):
        return all(value == 0 for value in funnel_data['number'])


    overall_Funnel_data = {
        'number': [
            current_funnel['Total_Sessions'].sum(),
            current_funnel['Total_Views'].sum(),
            current_funnel['Total_Cart'].sum(),
            current_funnel['Total_Orders'].sum()
        ],
        'stage': ["Total Sessions", "Total Views", "Total Cart", "Total Orders"],
        # 'user_type': current_funnel['user_type'].unique()
    }
    funnel_data_new = {
        'number': [
            new_user_funnel['Total_Sessions'].sum(),
            new_user_funnel['Total_Views'].sum(),
            new_user_funnel['Total_Cart'].sum(),
            new_user_funnel['Total_Orders'].sum()
        ],
        'stage': ["Total Sessions", "Total Views", "Total Cart", "Total Orders"],
        # 'user_type': current_funnel['user_type'].unique()
    }
    funnel_data_return = {
        'number': [
            returning_user_funnel['Total_Sessions'].sum(),
            returning_user_funnel['Total_Views'].sum(),
            returning_user_funnel['Total_Cart'].sum(),
            returning_user_funnel['Total_Orders'].sum()
        ],
        'stage': ["Total Sessions", "Total Views", "Total Cart", "Total Orders"],
        # 'user_type': current_funnel['user_type'].unique()
    }
    # st.write(funnel_data_return)
    with funnel_col1:
        # Create the funnel chart
        fig_overall = px.funnel(overall_Funnel_data, x='number', y='stage', color_discrete_sequence=returning_user_colors)
        fig_overall.update_layout(
            title={
            'text': 'Over all Funnel',
            'x': 0.6,
            'xanchor': 'center'
                    },
        )
        st.plotly_chart(fig_overall, use_container_width=True, config=config)

    with funnel_col2:
        if not is_all_zero(funnel_data_new):
            fig_new_user = px.funnel(funnel_data_new, x='number', y='stage', color_discrete_sequence=new_user_colors,)
            fig_new_user.update_layout(yaxis=dict(visible=False),
                                        title={
                                                'text': 'New Users Funnel',
                                                'x': 0.5,
                                                'xanchor': 'center'
                                            },
                                    )
            st.plotly_chart(fig_new_user, use_container_width=True, config=config)

        else:
            st.write("Sorry there is No New User for that period")

    with funnel_col3:
        if not is_all_zero(funnel_data_return):
            fig_return_user = px.funnel(funnel_data_return, x='number', y='stage')
            fig_return_user.update_layout(yaxis=dict(visible=False),
                            title={
                                    'text': 'Returning Users Funnel',
                                    'x': 0.5,
                                    'xanchor': 'center'
                                },
                        ) 
            st.plotly_chart(fig_return_user, use_container_width=True, config=config)
            # st.write(funnel_data_return)

        else:
            st.markdown(
                    """
                    <div style="border: 2px solid; padding: 20px; background: linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%); text-align: center;">
                        <strong><p style="margin: 0; color: white;">Sorry No Returning Users for that Period</p></strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    #################### Bar Columns #############################

    figure_sessions, figure_orders = st.columns(2)
    
    unique_categories = category_data_markdown['category'].unique()

    with figure_sessions:
        sessions_fig_bar = px.bar(
                data_frame=category_data_sessions,
                x='category',
                y='Sessions',  # Separate bars for new and returning users
                color='user_type',  # Assign colors for better differentiation
                title='Sessions of New and Returning Users by Category over time',
                labels={'value': 'Count', 'category': 'Category', 'variable': 'User Type'},
                barmode='group',
                color_discrete_sequence = [new_user_colors[0], '#00d4ff',],
                height=500
        )
        sessions_fig_bar.update_layout(
            showlegend=False,
            title={
                'text': 'Sessions of New and Returning Users by Category over time',
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        sessions_fig_bar.update_traces(texttemplate='%{y:.2s}', textposition='outside')
        st.plotly_chart(sessions_fig_bar, use_container_width=True, config=config)

    with figure_orders:
        orders_fig_bar = px.bar(
                data_frame=category_data_orders,
                x='category',
                y='Orders',  # Separate bars for new and returning users
                color='user_type',  # Assign colors for better differentiation
                # title='Orders of New and Returning Users by Category over time',
                labels={'value': 'Count', 'category': 'Category', 'variable': 'User Type'},
                barmode='group',
                color_discrete_sequence = [new_user_colors[0], '#00d4ff'],
                height=500
                
        )
        orders_fig_bar.update_layout(
            showlegend=False,
            title={
                'text': 'Orders of New and Returning Users by Category over time',
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        orders_fig_bar.update_traces(texttemplate='%{y:.2s}', textposition='outside')
        st.plotly_chart(orders_fig_bar, use_container_width=True, config=config)



    with st.container(height=250):
        st.write("Minimum and Maximum Sessions Per Category in selected Period")
        for category in unique_categories:
            data = category_data_markdown[category_data_markdown['category'] == category]

            max_row_sessions = data.loc[data['Total_Sessions'].idxmax()]
            min_row_sessions = data.loc[data['Total_Sessions'].idxmin()]
            average_sessions = data['Total_Sessions'].mean()

            max_row_cart = data.loc[data['Total_Cart'].idxmax()]
            min_row_cart = data.loc[data['Total_Cart'].idxmin()]
            average_cart = data['Total_Cart'].mean()

            max_row_order = data.loc[data['Total_Orders'].idxmax()]
            min_row_order = data.loc[data['Total_Orders'].idxmin()]
            average_order = data['Total_Orders'].mean()

            max_row_sales = data.loc[data['Total_Sales'].idxmax()]
            min_row_sales = data.loc[data['Total_Sales'].idxmin()]
            average_sales = data['Total_Sales'].mean()


            st.markdown(f"""
                        <div style='border: 2px solid #51829B; padding: 5px; margin-bottom: 5px; width: auto;'>
                            <b><h6 style='font-size: 20px; text-align: center;  margin-bottom: 0; margin-top: 10px;'>{category.title()}</h6></b><br>
                            <hr style='border-top: 2px solid #51829B; margin-bottom: 5px; margin-top: 0px;'> <!-- Horizontal line -->
                            <b>Min Sessions:</b> {min_row_sessions['Total_Sessions']:,.0f} on <b>{min_row_sessions['date']}</b><br>
                            <b>Max Sessions:</b> {max_row_sessions['Total_Sessions']:,.0f} on <b>{max_row_sessions['date']}</b><br>
                            <b>Average Sessions:</b> {average_sessions:,.2f}<br>
                            <b>Min Cart:</b> {min_row_cart['Total_Cart']:,.0f} on <b>{min_row_cart['date']}</b><br>
                            <b>Max Cart:</b> {max_row_cart['Total_Cart']:,.0f} on <b>{max_row_cart['date']}</b><br>
                            <b>Average Cart:</b> {average_cart:,.2f}<br>
                            <b>Min Order:</b> {min_row_order['Total_Orders']:,.0f} on <b>{min_row_order['date']}</b><br>
                            <b>Max Order:</b> {max_row_order['Total_Orders']:,.0f} on <b>{max_row_order['date']}</b><br>
                            <b>Average Order:</b> {average_order:,.2f}<br>
                            <b>Min Sales:</b> {min_row_sales['Total_Sales']:,.0f} on <b>{min_row_sales['date']}</b><br>
                            <b>Max Sales:</b> {max_row_sales['Total_Sales']:,.0f} on <b>{max_row_sales['date']}</b><br>
                            <b>Average Sales:</b> $ {average_sales:,.2f}<br>
                        </div>
                        """
            , unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='border: 2px solid #0047ab; min-height: 50px; display: block; text-align: center; background: linear-gradient(45deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%);'><h2 style= 'color: white;'> Days the Contributed 70% of orders per period</h2></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    try:
        fig_trend_line = px.scatter(data_70_percent, x='date', y='Orders', trendline="lowess", title='Orders Trend Over Time')

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
            x=extreme_points['date'],
            y=extreme_points['Orders'],
            mode='markers',
            marker=dict(color='red', size=10),
            name='Extreme Points'
        ))

        # Update the trend line color to purple
        for trace in fig_trend_line.data:
            if trace.mode == 'lines':
                trace.line.color = '#800080'
    except:
        fig_trend_line = px.scatter(data_70_percent, x='date', y='Orders', title='Orders Trend Over Time')


    st.plotly_chart(fig_trend_line, use_container_width=True, config=config)

    pareto_fig = px.bar(top_performing_cat_without_elec_unk, x='category', y='Total_Sales', title='Categories contributed the most to sales ex electronics and unknown')
    pareto_fig.add_scatter(x=top_performing_cat_without_elec_unk['category'], y=top_performing_cat_without_elec_unk['Cum_perc'], yaxis='y2')

    pareto_fig.update_layout(
        yaxis2=dict(
            title='Cumulative Percentage',
            overlaying='y',
            side='right',
            tickmode='array',
            tickvals=[i*10 for i in range(11)],
            ticktext=[f'{i*10}%' for i in range(11)],
            showgrid=False
        )
    )
    pareto_fig.update_traces(texttemplate='%{y:.2s}', textposition='outside', selector=dict(type='bar'))
    st.plotly_chart(pareto_fig, use_container_width=True, config=config)

    
    custom_order = ["Star", "High Performance", "Low Performance", "Weak Performance"]
    with st.container():
        selected_bucket = st.radio("Select Score Bucket:", options=custom_order, horizontal= True)
        filtered_brand = class_result[class_result['Score_Bucket'] == selected_bucket]
        

        # Create scatter plot
        buckets = px.scatter(filtered_brand, x='brand', y='Orders', color='Orders',
                        hover_data=['brand', 'Views', 'Sales'], size='Orders',
                        title='Brand Evaluation Scatter Plot')
        # buckets.update_layout(scattermode='group')
        st.plotly_chart(buckets, use_container_width=True, config=config)
    st.divider()
    filtered_brand = filtered_brand.sort_values(by='Sales', ascending=False)
    st.dataframe(filtered_brand, hide_index=True, column_order=['brand', 'Views', 'Sales', 'Orders', 'Buyers'], use_container_width=True)
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        custom_order = ["Star", "High Performance", "Low Performance", "Weak Performance"]
        cat_selected_bucket = st.radio("Select Bucket:", options=custom_order, horizontal= True)
    with filter_col2:
        user_options = {"All Users" : "All Users" ,"New_User": "New User", "Returning_User": "Returning User"}
        reverse_user_options = {v: k for k, v in user_options.items()}
        selected_user_name = st.radio("Select User Type:", options=list(user_options.values()), horizontal= True)
        selected_user = reverse_user_options[selected_user_name]

    # Selectbox for additional option
    available_brands = abndon_df[abndon_df['Score_Bucket'] == cat_selected_bucket].sort_values(by='Sales', ascending=False)['brand'].unique()
    selectbox_options = list(available_brands)
    selected_option = st.selectbox("Select an option (or leave unselected):", options=["All Brands"] + selectbox_options, index=0)



    
    if selected_user == "All Users" and selected_option != "All Brands":
        filtered_abn = abndon_df[(abndon_df['Score_Bucket'] == cat_selected_bucket) & (abndon_df['brand'] == selected_option) &(abndon_df['user_type'].isin(['New_User', 'Returning_User']))]

        filtered_abn = filtered_abn.copy()
        filtered_abn['date'] = filtered_abn['date'].dt.date
        brand_bar_fig = px.bar(filtered_abn, x='date', y='Abandonment Rate', color='user_type', barmode='group', color_discrete_sequence = [ new_user_colors[0], '#00d4ff'])
        brand_bar_fig.update_layout(xaxis_title='Date', xaxis_tickformat='%Y-%m-%d', showlegend=True)
        brand_bar_fig.update_traces(texttemplate='%{y:.2s}%', textposition='outside')
        st.plotly_chart(brand_bar_fig, use_container_width=True, config=config)

    elif selected_user != "All Users" and selected_option != "All Brands":
        filtered_abn = abndon_df[(abndon_df['user_type'] == selected_user) & (abndon_df['Score_Bucket'] == cat_selected_bucket) & (abndon_df['brand'] == selected_option)]
        bran_line_fig = px.line(filtered_abn, x = 'date', y = 'Abandonment Rate', title=f"Abandomnet Cart Rate for {selected_option} brand and User type {selected_user_name}")
        st.plotly_chart(bran_line_fig, use_container_width=True, config=config)

    elif selected_user == "All Users" and selected_option == "All Brands":
        filtered_abn = abndon_df[(abndon_df['Score_Bucket']==cat_selected_bucket)]   
        
        abn_brand_fig = px.scatter(filtered_abn, x='brand', y='Abandonment Rate', color='user_type',
                        hover_data=['brand', 'Views', 'Sales'], size='Abandonment Rate',
                        title='Abandonment Cart Rate for Brands by User Type Scatter Plot', color_discrete_sequence = [  new_user_colors[0], '#00d4ff',])
        st.plotly_chart(abn_brand_fig, use_container_width=True, config=config)

    elif selected_user == "New_User" and selected_option == "All Brands":
        filtered_abn = abndon_df[(abndon_df['Score_Bucket']==cat_selected_bucket) & (abndon_df['user_type']==selected_user)]
        abn_brand_fig = px.scatter(filtered_abn, x='brand', y='Abandonment Rate', color='Abandonment Rate',
                        hover_data=['brand', 'Views', 'Sales'], size='Abandonment Rate', color_discrete_sequence = [ new_user_colors[0]],
                        title='Abandonment Cart Rate for Brands by New User Scatter Plot')
        st.plotly_chart(abn_brand_fig, use_container_width=True, config=config)

    elif selected_user == "Returning_User" and selected_option == "All Brands":
        filtered_abn = abndon_df[(abndon_df['Score_Bucket']==cat_selected_bucket) & (abndon_df['user_type']==selected_user)]
        abn_brand_fig = px.scatter(filtered_abn, x='brand', y='Abandonment Rate', color='Abandonment Rate',
                        hover_data=['brand', 'Views', 'Sales'], size='Abandonment Rate', color_discrete_sequence = [ new_user_colors[0]],
                        title='Abandonment Cart Rate for Brands by Returning User Scatter Plot')
        st.plotly_chart(abn_brand_fig, use_container_width=True, config=config)
    st.divider()
    filtered_abn['date'] = pd.to_datetime(filtered_abn['date']).dt.date
    # filtered_abn['date'] = filtered_abn['date'].dt.date.copy()
    st.dataframe(filtered_abn, use_container_width=True, column_order=['date', 'brand', 'Views', 'Orders', 'Sales', 'Buyers', 'Score_Bucket', 'Abandonment Rate'])


if __name__ == "__main__":
    app()
