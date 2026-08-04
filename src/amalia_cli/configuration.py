import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")

        if not self.api_key:
            raise ValueError("API_KEY is not configured.")

        if not self.base_url:
            raise ValueError("BASE_URL is not configured.")

        if not self.model:
            raise ValueError("MODEL is not configured.")