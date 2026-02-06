from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from models.error_log import ErrorLog
from models.utilities import Utilities
import config.config as config

class Notification:
    @staticmethod
    def send_daily_first_notification():
        try:
            body = f"{config.GMAIL_DAILY_FIRST_MESSAGE}\n\n検知時間: {Utilities.get_timestamp()}"
            message = MIMEMultipart()
            message["From"] = config.GMAIL_SENDER
            message["To"] = config.GMAIL_RECEIVER
            message["Subject"] = config.GMAIL_DAILY_FIRST_SUBJECT
            
            message.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(config.GMAIL_SERVER, config.GMAIL_SMTP_ADDRESS) as server:
                server.starttls()
                server.login(config.GMAIL_SENDER, config.APP_PASSWORD)
                server.send_message(message)
        except Exception as error:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "GMAIL", error = f"{error}")
    
    @staticmethod
    def send_error_notification(timestamp: str, error_type: str, error: str):
        try:
            body = f"{config.GMAIL_ERROR_MESSAGE}\n\nエラータイプ: {error_type}\nエラー内容: {error}\n発生時間: {timestamp}"
            message = MIMEMultipart()
            message["From"] = config.GMAIL_SENDER
            message["To"] = config.GMAIL_RECEIVER
            message["Subject"] = config.GMAIL_ERROR_SUBJECT
            
            message.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(config.GMAIL_SERVER, config.GMAIL_SMTP_ADDRESS) as server:
                server.starttls()
                server.login(config.GMAIL_SENDER, config.APP_PASSWORD)
                server.send_message(message)
        except Exception as error:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "GMAIL", error = f"{error}")
