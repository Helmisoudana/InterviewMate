import uvicorn
from fastapi import FastAPI
from storage.api.api import router

app = FastAPI(title="InterviewMate API")

# On inclut le routeur
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)