from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.api.models import OccurrenceRequest, OccurrenceResponse, StatusResponse
from src.api.storage import storage
from src.services.occurrence_processor import process_occurrence_async

router = APIRouter()


@router.post("/handle_occurrence", response_model=OccurrenceResponse)
async def handle_occurrence(request: OccurrenceRequest, background_tasks: BackgroundTasks):
    try:
        hash_id = storage.create_occurrence(request.model_dump())

        background_tasks.add_task(
            process_occurrence_async,
            hash_id,
            request.model_dump(),
            request.scenario
        )

        return OccurrenceResponse(hash=hash_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar ocorrência: {str(e)}")


@router.get("/status_occurrence", response_model=StatusResponse)
async def get_status_occurrence(hash: str):
    occurrence = storage.get_occurrence(hash)

    if not occurrence:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada")

    return StatusResponse(
        status_final=occurrence.status,
        mensagens=occurrence.messages
    )
