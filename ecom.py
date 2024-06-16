import streamlit as st
from pages import sessions, category
from components.add_ga import inject_ga

st.set_page_config(layout='wide', page_title='Ecom-Dashboard', initial_sidebar_state='collapsed')
no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem}</style>', unsafe_allow_html=True)


# inject_ga()

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

    contact_form = """
    <form id="contactform" action="https://formsubmit.co/a57941acbd31d4e9912eb3042be91c08" method="POST">
        <label for="name">Name:</label>
        <input name="name" placeholder="Your Name" type="text" id="name" required>
        <br>
        <label for="email">Email:</label>
        <input name="email" placeholder="Your Email" type="email" id="email" required>
        <br>
        <label for="comment">Comment:</label>
        <textarea name="comment" placeholder="Your Message Here" id="comment" rows="3" required></textarea>
        <br>
        <input name="_formsubmit_id" type="text" style="display:none">
        <input value="Submit" type="submit">
    </form>
    """
    with st.container(border=True):
        st.write("Contact Your Analyst")
        st.markdown(contact_form, unsafe_allow_html=True)

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    local_css("components/style.css")

    st.title("Innovative Solutions Across Industries")
    
   
    tabs = ['Ecom Dashboard', "Categories", "Customers"]
    tab_selection = st.tabs(tabs)

    with tab_selection[0]:
        sessions.app()
        # testing.app()

    with tab_selection[1]:
        category.app()

    # with tab_selection[2]:
        


if __name__ == '__main__':
    
    main()