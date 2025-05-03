import datetime
from fastapi import Request
from fastapi.security import OAuth2

from database import get_user_by_id
from security import NotAuthenticatedError, decrypt_access_token
from schemas import UserJwt

class OAuthCookieSecure(OAuth2):
    async def __call__(self, request: Request) -> int | str | None:
        data = decrypt_access_token(request.cookies.get("access_token"))
        if data is None or not (user := await get_user_by_id(data['sub'])):
            raise NotAuthenticatedError()
        return user


class OAuthUserCookie(OAuth2):
    async def __call__(self, request: Request) -> UserJwt | None:
        data = decrypt_access_token(request.cookies.get("access_token"))
        if data is None:
            return None
        user = UserJwt(id=data['sub'],first_name=data['name'])
        return user
    
oauth_cookie = OAuthCookieSecure()
current_user_from_jwt = OAuthUserCookie()

def get_current_year():
    return datetime.datetime.now().year