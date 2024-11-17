from secrets import token_urlsafe

from envparse import env


env.read_envfile()

JWT_SECRET_KEY = token_urlsafe(32)
JWT_ALGORITHM = "HS256"
MONGO_URL = env.str("MONGO_URL")
