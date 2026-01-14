import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from models.error_log import ErrorLog
from models.utilities import Utilities
import config.config as config

class Notification:
    @staticmethod
    def _get_credentials():
        creds = None

        if os.path.exists(config.GMAIL_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(config.GMAIL_TOKEN_FILE, config.GMAIL_SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(config.GMAIL_CREDENTIALS_FILE, config.GMAIL_SCOPES)
                creds = flow.run_local_server(port = 0)
            with open(config.GMAIL_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials = creds)
        return service

    @staticmethod
    def send_daily_first_notification():
        service = Notification._get_credentials()
        try:
            message = MIMEText(config.GMAIL_DAILY_FIRST_MESSAGE)
            message['To'] = config.GMAIL_RECEIVER
            message['From'] = config.GMAIL_SENDER
            message['Subject'] = config.GMAIL_DAILY_FIRST_SUBJECT
            message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            message = service.users().messages().send(userId = "me", body = message).execute()
        except HttpError as error:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "GMAIL", error = f"{error}")
    
    @staticmethod
    def send_error_notification():
        pass
