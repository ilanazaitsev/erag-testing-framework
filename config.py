import os
from dotenv import load_dotenv

load_dotenv()

ZEPHYR_API_URL = os.getenv("ZEPHYR_API_URL")
ZEPHYR_API_TOKEN = os.getenv("ZEPHYR_API_TOKEN")
TEST_CYCLE_NUMBER = os.getenv("TEST_CYCLE_NUMBER")