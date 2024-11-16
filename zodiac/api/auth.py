# auth.py
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from blacksheep.server.authentication import AuthenticationHandler
from blacksheep.messages import Request
from blacksheep.exceptions import Unauthorized
from passlib.hash import bcrypt
from zodiac.config import JWT_ALGORITHM, JWT_SECRET_KEY
from zodiac.entities.db.user import User

async def authenticate_user(email: str, password: str) -> Optional[User]:
    user = await User.find_one(User.email == email)
    if user and bcrypt.verify(password, user.password_hash):
        return user
    return None

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

class JWTAuthenticationHandler(AuthenticationHandler):
    async def authenticate(self, context: Request):
        auth_header = context.headers.get(b"Authorization")
        if not auth_header:
            return None  # No authentication provided

        try:
            auth_header_value = auth_header.decode()
            scheme, _, token = auth_header_value.partition(' ')
            if scheme.lower() != 'bearer':
                raise Unauthorized("Invalid authentication scheme")

            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                raise Unauthorized("Invalid token payload")

            user = await User.get(user_id)
            if user:
                # Set the identity on the request
                context.identity = user
                return user
            else:
                raise Unauthorized("User not found")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise Unauthorized("Invalid or expired token")

# Instantiate the authentication handler
jwt_authentication_handler = JWTAuthenticationHandler()
