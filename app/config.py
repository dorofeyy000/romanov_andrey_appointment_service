import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/romanov_andrey_variant3"
)
APP_PORT=int(os.getenv("APP_PORT","8000"))
SECRET_KEY=os.getenv("SECRET_KEY","change_me")
