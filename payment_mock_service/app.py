import argparse

import uvicorn
from fastapi import FastAPI
from routes.v1.payments import router as payments_router

app = FastAPI(title="Payment Mock Service", version="1.0.0")

app.include_router(payments_router, prefix="/api/payments")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
