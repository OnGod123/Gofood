import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email, subject, body, html_body=None):
    """
    Sends an email using SMTP.
    """
    mail_server = current_app.config["MAIL_SERVER"]
    mail_port = current_app.config["MAIL_PORT"]
    mail_username = current_app.config["MAIL_USERNAME"]
    mail_password = current_app.config["MAIL_PASSWORD"]
    mail_sender = current_app.config["MAIL_DEFAULT_SENDER"][1]

    # --- Create the message ---
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{current_app.config['MAIL_DEFAULT_SENDER'][0]} <{mail_sender}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    # --- Send the email ---
    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()  # Secure the connection
            server.login(mail_username, mail_password)
            server.send_message(msg)
            print(f"[EMAIL] Sent to {to_email}")
            return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

