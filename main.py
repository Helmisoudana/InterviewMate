import uvicorn
from fastapi import FastAPI
from storage.api.api import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="InterviewMate API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)