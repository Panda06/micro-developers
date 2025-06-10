import argparse

import uvicorn
from fastapi import FastAPI
from routes.v1.bills import router as bills_router

app = FastAPI(title="Billing Service", version="1.0.0")

app.include_router(bills_router, prefix="/api/bills")


@app.get("/")
async def root():
    return {"message": "Billing Service"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
