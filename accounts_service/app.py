import argparse

import uvicorn
from fastapi import FastAPI
from routes.v1.accounts import router as accounts_router

app = FastAPI(title="Accounts Management Service", version="1.0.0")

app.include_router(accounts_router, prefix="/api/accounts")


@app.get("/")
async def root():
    return {"message": "Accounts Management Service"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
