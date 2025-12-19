import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE設定
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
API_NAME = os.getenv("API_NAME")

# DIRECTORY設定
TEMP_DIR = os.getenv("TEMP_DIR")
