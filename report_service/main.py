from fastapi import FastAPI
from api.receipt import router as receipt_router

app = FastAPI(title="Report Service")

app.include_router(receipt_router, prefix='/api/receipt')