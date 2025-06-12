from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_keycloak import FastAPIKeycloak, OIDCUser
from dotenv import load_dotenv
from pydantic import SecretStr, BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn, httpx, os

load_dotenv()

app = FastAPI()

idp = FastAPIKeycloak(
    server_url=os.getenv("KEYCLOAK_BASE_URL"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    admin_client_secret=os.getenv("ADMIN_CLIENT_SECRET"),
    realm=os.getenv("KEYCLOAK_REALM"),
    callback_uri=os.getenv("CALLBACK_URI"),
)
idp.add_swagger_config(app)


def keycloak_token_url():
    return f"{os.getenv('KEYCLOAK_BASE_URL')}/realms/{os.getenv('KEYCLOAK_REALM')}/protocol/openid-connect/token"


async def refresh_access_token(refresh_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            keycloak_token_url(),
            data={
                "grant_type": "refresh_token",
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to refresh token")

        return response.json()


class TokenCookieToHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")

        if token:
            request.headers.__dict__["_list"].append(
                (b"authorization", f"Bearer {token}".encode())
            )

        response = await call_next(request)

        if response.status_code == 401:
            refresh_token = request.cookies.get("refresh_token")
            if refresh_token:
                try:
                    tokens = await refresh_access_token(refresh_token)
                    new_access_token = tokens["access_token"]
                    new_refresh_token = tokens.get("refresh_token", refresh_token)

                    request.headers.__dict__["_list"].append(
                        (b"authorization", f"Bearer {new_access_token}".encode())
                    )

                    response = await call_next(request)

                    response.set_cookie(
                        key="access_token",
                        value=new_access_token,
                        httponly=True,
                        secure=False,
                        samesite="Lax",
                    )
                    response.set_cookie(
                        key="refresh_token",
                        value=new_refresh_token,
                        httponly=True,
                        secure=False,
                        samesite="Lax",
                    )

                except Exception:
                    return RedirectResponse(idp.login_uri)

        return response


app.add_middleware(TokenCookieToHeaderMiddleware)


@app.get("/")
def root():
    return "Hello World"


@app.get("/user")
def get_current_user(user: OIDCUser = Depends(idp.get_current_user())):
    return user


@app.get("/login")
def login_redirect():
    return RedirectResponse(idp.login_uri)


@app.get("/callback")
def callback(session_state: str, code: str):
    tokens = idp.exchange_authorization_code(session_state=session_state, code=code)
    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    response = RedirectResponse(url="/user")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
    )
    return response


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: SecretStr


@app.post("/users", tags=["user-management"])
def create_user(user: UserCreate):
    return idp.create_user(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.email,
        email=user.email,
        password=user.password.get_secret_value(),
        send_email_verification=False,
    )


@app.put("/user/{user_id}/change-password", tags=["user-management"])
def change_password(user_id: str, new_password: SecretStr):
    return idp.change_password(
        user_id=user_id, new_password=new_password.get_secret_value()
    )


@app.delete("/user/{user_id}", tags=["user-management"])
def delete_user(user_id: str):
    return idp.delete_user(user_id=user_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
