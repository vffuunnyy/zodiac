from secrets import token_urlsafe
from envparse import env

JWT_SECRET_KEY = token_urlsafe(32)
JWT_ALGORITHM = "HS256"
MONGO_URL = "123" or env.str("MONGO_URL")