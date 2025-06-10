# auth_router.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from config import settings
from services.keycloack_client import KeyCloackClient
from services.auth_dep import get_keycloak_client, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
def login():
    auth_url = (
        f"{settings.auth_url}"
        f"?client_id={settings.CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={settings.redirect_uri}"
    )
    return RedirectResponse(auth_url)


@router.get("/login/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    keycloak: KeyCloackClient = request.app.state.keycloak_client
    tokens = await keycloak.get_tokens(code)
    
    response = RedirectResponse(url="/auth/me")
    response.set_cookie("access_token", tokens["access_token"], httponly=True)
    return response

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": user}


@router.get("/logout")
def logout():
    logout_url = (
        f"{settings.logout_url}"
        f"?client_id={settings.CLIENT_ID}"
        f"&post_logout_redirect_uri={settings.BASE_URL}"
    )
    response = RedirectResponse(logout_url)
    response.delete_cookie("access_token")
    return response
