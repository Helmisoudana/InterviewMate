import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from storage.api.api import router
from scoring.api.scoring_router import router as scoring_router

# 1. Créer le dossier "logs" s'il n'existe pas
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "main.log")

# 2. Configurer le logging de Python pour écrire UNIQUEMENT dans le fichier (pas de StreamHandler)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ]
)

app = FastAPI(title="InterviewMate API", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(scoring_router)

if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG

    log_config["handlers"]["file_handler"] = {
        "class": "logging.FileHandler",
        "filename": LOG_FILE,
        "mode": "a",
        "formatter": "default",
        "encoding": "utf-8"
    }

    # Rediriger tous les loggers d'Uvicorn uniquement vers le fichier
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        log_config["loggers"][logger_name]["handlers"] = ["file_handler"]

    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        log_config=log_config
    )