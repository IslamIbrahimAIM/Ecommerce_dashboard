import streamlit as st
# from pages import customers, sales, testing
from pages import customers, sales, overview

st.set_page_config(layout='wide', page_title='Ecom-Dashboard')
st.markdown('<style>div.block-container{padding-top:1rem}</style>', unsafe_allow_html=True)

def main():
    """ 
    Testing Streamlit
    """
    # Sidebar Navigation
    st.title("Ecom_Dashboard")
    st.subheader('Hello Islam')
    

    # Define tabs
    # tabs = ['Dashboard', "Sales", "Customers"]
    tabs = ['Dashboard', "Sales", "Customers"]
    tab_selection = st.tabs(tabs)

    with tab_selection[0]:
        overview.app()
        # testing.app()

    with tab_selection[1]:
        sales.app()

    with tab_selection[2]:
        customers.app()


if __name__ == '__main__':
    
    main()


