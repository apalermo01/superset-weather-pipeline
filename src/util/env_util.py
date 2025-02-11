from dotenv import load_dotenv
import os

load_dotenv()

def get_env(name):
    return os.getenv(name, 'NONE')
