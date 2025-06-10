from fastapi import FastAPI
from services.auth_router import router
from services.keycloack_client import KeyCloackClient

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.keycloak_client = KeyCloackClient()

app.include_router(router)
