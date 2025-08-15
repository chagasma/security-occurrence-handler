import uvicorn
from fastapi import FastAPI
from src.api.endpoints import router

app = FastAPI(title="Security Occurrence Handler", version="1.0.0")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
