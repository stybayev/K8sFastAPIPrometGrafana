import os
import importlib

from dotenv import load_dotenv

load_dotenv()

module = importlib.import_module(os.getenv("USER_CLASS"))
user_class = getattr(module, os.getenv("USER_CLASS"))
