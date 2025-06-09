from fastapi import FastAPI

app = FastAPI(title="Report Service")

@app.get("/")
async def root():
    return {"message": "Hello World"}