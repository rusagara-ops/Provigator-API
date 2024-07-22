from fastapi import FastAPI, Depends, HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY
from fastapi.security import OAuth2PasswordBearer


config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id = config('GOOGLE_CLIENT_ID'),
    client_secret = config('GOOGLE_CLIENT_SECRET'),
    authorize_url = "https://accounts.google.com/o/oauth2/auth",
    access_token_url = "https://accounts.google.com/o/oauth2/token",
    client_kwargs = {"scope": "email profile"},
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    authorize_state = SECRET_KEY,
)

app = FastAPI()

SECRET_KEY = config('SECRET_KEY', default='yGOCSPX-MqjF7UVPZDkjih56G6r4EHKDOwUh')
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_db = {}
    

