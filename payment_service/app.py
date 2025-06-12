import argparse
import logging

import uvicorn
from fastapi import FastAPI
from routes.v1.payments import router as payments_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("payment_service")

app = FastAPI(title="Payment Service", version="1.0.0")

app.include_router(payments_router, prefix="/api/payments")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Payment Service"}


@app.on_event("startup")
async def startup_event():
    logger.info("Payment Service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Payment Service shutting down...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    logger.info(f"Starting Payment Service on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
