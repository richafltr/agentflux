import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    SCREENSHOT_WIDTH = int(os.getenv("SCREENSHOT_WIDTH", "1920"))
    SCREENSHOT_HEIGHT = int(os.getenv("SCREENSHOT_HEIGHT", "1080"))
    SCREENSHOT_TIMEOUT = int(os.getenv("SCREENSHOT_TIMEOUT", "30000"))
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return True 