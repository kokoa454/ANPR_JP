import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE設定
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
API_NAME = os.getenv("API_NAME")

#TIMESTAMP設定
TIME_STAMP_FORMAT = os.getenv("TIME_STAMP_FORMAT")