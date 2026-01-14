import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.error_log import ErrorLog
from models.utilities import Utilities

class Notification:
    @staticmethod
    def _get_credentials():
        flow = InstalledAppFlow.from_client_secrets_file(config.GMAIL_CREDENTIALS_FILE, config.GMAIL_SCOPES)
        creds = flow.run_local_server(port=0)
        service = build('gmail', 'v1', credentials=creds)
        return service

    @staticmethod
    def send_daily_first_notification():
        service = Notification._get_credentials()
        try:
            message = {
                "to": config.GMAIL_RECEIVER,
                "subject": "Daily First Notification",
                "body": f"Daily First Notification\n\n{Utilities.get_timestamp()}"
            }
            message = service.users().messages().send(userId = "me", body = message).execute()
        except HttpError as error:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "GMAIL", error = f"{error}")
    
    @staticmethod
    def send_error_notification():
        pass
