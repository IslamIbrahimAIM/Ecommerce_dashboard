import os
import streamlit as st
from pages import sessions, category
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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

    # contact_form = """
    # <form id="contactform" action="https://formsubmit.co/a57941acbd31d4e9912eb3042be91c08" method="POST">
    #     <label for="name">Name:</label>
    #     <input name="name" placeholder="Your Name" type="text" id="name" required>
    #     <br>
    #     <label for="email">Email:</label>
    #     <input name="email" placeholder="Your Email" type="email" id="email" required>
    #     <br>
    #     <label for="comment">Comment:</label>
    #     <textarea name="comment" placeholder="Your Message Here" id="comment" rows="3" required></textarea>
    #     <br>
    #     <input name="_formsubmit_id" type="text" style="display:none">
    #     <input value="Submit" type="submit">
    # </form>
    # """
    # with st.container(border=True):
    #     st.write("Contact Your Analyst")
    #     st.markdown(contact_form, unsafe_allow_html=True)


    st.title('Contact Form')

    # Input fields
    name = st.text_input('Your Name')
    email = st.text_input('Your Email')
    subject = st.text_input('Subject')
    message = st.text_area('Message', height=200)

    if st.button('Send Email'):
        # Logic to send email
        if name and email and subject and message:
            # SMTP server configuration for Gmail
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587  # Gmail SMTP port
            smtp_username = os.getenv('USER_NAME')  # your Gmail address
            smtp_password = os.getenv('PASSWARD')  # your Gmail password or app-specific password

            # Email content
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = smtp_username  # your Gmail address
            msg['Subject'] = subject
            
            # Attach message
            msg.attach(MIMEText(f"Name: {name}\nEmail: {email}\n\n{message}", 'plain'))

            try:
                # Establishing SMTP connection
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()  # Secure the connection
                    server.login(smtp_username, smtp_password)  # Login
                    server.sendmail(email, smtp_username ,msg.as_string())  # Send email
                    server.quit()
                    st.success('Email sent successfully!')
            except Exception as e:
                st.error(f'Error: {e}')
        else:
            st.warning('Please fill in all fields.')


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