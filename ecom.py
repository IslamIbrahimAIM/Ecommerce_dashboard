import os
import streamlit as st
from pages import sessions, category
import streamlit.components.v1 as components
from components.contact_form import send_email_with_auto_reply
# from components.add_ga import inject_ga


st.set_page_config(layout='wide', page_title='Ecom-Dashboard', initial_sidebar_state='collapsed')
no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
# Include Google Analytics tracking code
with open("google_analytics.html", "r") as f:
    html_code = f.read()
    components.html(html_code, height=0)

# inject_ga()
# load_dotenv()

st.markdown(no_sidebar_style, unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem}</style>', unsafe_allow_html=True)




st.cache_data.clear()
def main():
    """ 
    Testing Streamlit
    """

    # Replace with your LinkedIn profile URL
    linkedin_url = "https://www.linkedin.com/in/islamabdallam/"
    linkedin_icon_markdown = f'<a href="{linkedin_url}" target="_blank"><img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" style="border:50%;  width: 70px; height: 50px;"></a>'
    
    # Display LinkedIn icon as markdown
    st.markdown(linkedin_icon_markdown, unsafe_allow_html=True)

    # Apply custom CSS to change the button color
    st.markdown(
        """
        <style>
        .stButton button {
            background-color: green;
            color: white;
        }
        .stButton button:hover {
            background-color: transparent;

        }
        </style>
        """,
        unsafe_allow_html=True
    )


    def check_form(name, subject, email, message):
        if not name:
            st.warning("Please enter your Name")
            return False
        if not subject:
            st.warning("Please enter a Subject")
            return False
        if not email:
            st.warning("Please enter your Email Address")
            return False
        if not message:
            st.warning("Please enter your Message")
            return False
        return True
    with st.expander(label="Contact Your Analyst"):
        with st.form("Contact Your Analyst", clear_on_submit=True):
            # title = st.markdown('**Contact your Analyst**')
            name = st.text_input(label="Name", placeholder="Please enter your Name")
            subject = st.text_input(label='Subject', placeholder="Please enter subject")
            email = st.text_input(label='Email Address', placeholder="Please enter your email:'abc@email.com'")
            message = st.text_area(label='Message', placeholder="Enter your Message Here")
            submit_msg = st.form_submit_button(label="Send Message")


    if submit_msg:
        if check_form(name, subject, email, message):
            success, message = send_email_with_auto_reply(name, subject, email, message)
            if success:
                st.success(message)
            else:
                st.error(message)

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    local_css("components/style.css")

    st.title("Innovative Solutions Across Industries")
    
   
    tabs = ['Ecom Dashboard', "Univariate Analysis",]
    tab_selection = st.tabs(tabs)

    with tab_selection[0]:
        sessions.app()
        # testing.app()

    with tab_selection[1]:
        category.app()

    # with tab_selection[2]:
        


if __name__ == '__main__':
    
    main()