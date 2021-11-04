import os
#from dotenv import load_dotenv
import smtplib
# load_dotenv(".env")
#SENDER_EMAIL_ID = os.getenv("SENDER_EMAIL")
SENDER_EMAIL_ID = os.environ.get("SENDER_EMAIL")
#PASSWORD = os.getenv("BLOGIFY_EMAIL")
PASSWORD = os.environ.get("SENDER_PASSWORD")
#RECIVER_EMAIL_ID = os.getenv("SENDER_PASSWORD")
RECIVER_EMAIL_ID = os.environ.get("BLOGIFY_EMAIL")


class SendMail:
    def __init__(self, data: dict) -> None:
        message = ""
        for key in data:
            message += f"{key}:{data[key]}\n"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=SENDER_EMAIL_ID, password=PASSWORD)
            connection.sendmail(
                from_addr=SENDER_EMAIL_ID, to_addrs=RECIVER_EMAIL_ID, msg=f"subject:USER QUERY\n\n{message}")
