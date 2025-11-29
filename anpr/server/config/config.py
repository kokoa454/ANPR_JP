from dotenv import load_dotenv
import os

load_dotenv()

# DATABASE設定
API_KEY = os.getenv("API_KEY")
API_NAME = os.getenv("API_NAME")
