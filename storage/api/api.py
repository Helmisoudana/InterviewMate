from fastapi import APIRouter, HTTPException, Query, Response
from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository

# Instanciation du repository
repository = PostgresStorageRepository.creer_depuis_env()

router = APIRouter(prefix="/history")

@router.get("/")
async def get_liste(k: int = Query(default=3, ge=1, le=100)):
    try: 
        json_data = await repository.recuperer_entretiens(K=k)
        return Response(content=json_data, media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la récupération des entretiens : {str(e)}"
        )