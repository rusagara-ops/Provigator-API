from starlette.config import Config

config = Config(".env")


GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
SECRET_KEY = config("SECRET_KEY")