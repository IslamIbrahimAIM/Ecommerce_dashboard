import streamlit as st
from pages import customers, sales, overview

st.set_page_config(layout='wide')

def main():
    """ 
    Testing Streamlit
    """
    # Sidebar Navigation
    st.title("Ecom Dashboard")
    st.subheader('Hello Islam')
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Dashboard", "Sales", "Customers"])

        # Page Routing
    if selection == "Dashboard":
        overview.app()
    elif selection == "Sales":
        sales.app()
    elif selection == "Customers":
        customers.app()


if __name__ == '__main__':
    main()