# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import os

# def send_email(name, email, subject, message):
#     try:
#         # SMTP server configuration for Mailtrap
#         smtp_server = 'send.api.mailtrap.io'
#         smtp_port = 587  # Mailtrap SMTP port
#         smtp_username = os.getenv('USER_NAME')  # your Mailtrap username
#         smtp_password = os.getenv('PASSWARD')  # your Mailtrap password

#         # Email content
#         msg = MIMEMultipart()
#         msg['From'] = email
#         msg['To'] = 'innovativesolutions.989@gmail.com'  # your recipient email
#         msg['Subject'] = subject
        
#         # Attach message
#         body = f"Name: {name}\nEmail: {email}\n\n{message}"
#         msg.attach(MIMEText(body, 'plain'))

#         # Establishing SMTP connection and sending the email
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()  # Secure the connection
#             server.login(smtp_username, smtp_password)  # Login
#             server.sendmail(email, msg['To'], msg.as_string())  # Send email
#             server.quit()
#         return "Email sent successfully!"
#     except Exception as e:
#         server.quit()
#         return f"Error: {e}"


# import smtplib

# sender = "Private Person <mailtrap@demomailtrap.com>"
# receiver = "A Test User <innovativesolutions.989@gmail.com>"

# message = f"""\
# Subject: Hi Mailtrap
# To: {receiver}
# From: {sender}

# This is a test e-mail message."""

# with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
#     server.starttls()
#     server.login("api", "43f74a7552a3b55d2e6239954d867501")
#     server.sendmail(sender, receiver, message)
#     server.quit()

import streamlit as st
import smtplib

def send_email_with_auto_reply(name, subject, email, message_area):
    # Load SMTP secrets for sending initial email
    smtp_server = st.secrets["smtp"]["server"]
    smtp_port = st.secrets["smtp"]["port"]
    smtp_username = st.secrets["smtp"]["username"]
    smtp_password = st.secrets["smtp"]["password"]

    # Load SMTP secrets for auto-reply
    google_smtp_server = st.secrets['google']['google_smtp_server']
    google_smtp_port = st.secrets['google']['google_smtp_port']
    google_smtp_username = st.secrets['google']['google_smtp_username']
    google_smtp_password = st.secrets['google']['google_smtp_password']

    # Email details
    sender = "Private Person <mailtrap@demomailtrap.com>"
    receiver = "A Test User <innovativesolutions.989@gmail.com>"

    # Initial email to receiver
    form_message = f"""\
Subject: {subject}
To: {receiver}
From: {sender}
Reply-To: {email}

Name: {name}
Message: {message_area}
"""

    # Auto-reply to sender
    auto_reply_message = f"""\
Subject: Auto-Reply: Thank you for your message
To: {email}
From: {receiver}

Hi {name},

Thank you for reaching out.
We have received your message:

{message_area}

We will get back to you shortly.

Best regards,
Your Team
"""

    try:
        # Send initial email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender, receiver, form_message)

        # Send auto-reply
        with smtplib.SMTP(google_smtp_server, google_smtp_port) as gserver:
            gserver.starttls()
            gserver.login(google_smtp_username, google_smtp_password)
            gserver.sendmail(receiver, email, auto_reply_message)

        return True, "Emails sent successfully!"
    
    except Exception as e:
        return False, f'An error occurred: {e}'
