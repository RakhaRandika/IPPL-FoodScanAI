import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH", "./model/foodscan_model.h5")
SECRET_KEY = os.getenv("SECRET_KEY", "secret_foodscanai")
