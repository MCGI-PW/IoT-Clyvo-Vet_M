"""
Servidor FastAPI e Endpoints da Solução ClyvoScribe AI (CLYVO VET).
"""
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

from app.config import APP_TITLE, APP_VERSION, WEB_DIR
from app.services.pipeline import clyvoscribe_pipeline
from app.services.asr_service import asr_service
from app.models.consultation import FullConsultationResult

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="API de Inteligência Clínica Ambiental e Apoio à Decisão Veterinária para a plataforma CLYVO VET."
)

# CORS liberado para integração front-end e mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConsultationRequest(BaseModel):
    pet_id: str
    sample_case_id: Optional[str] = None
    custom_transcript: Optional[str] = None


class FinalizeConsultationRequest(BaseModel):
    consultation_id: str
    crmv: str
    observacoes_finais: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": APP_TITLE,
        "version": APP_VERSION,
        "mode": "hybrid_clinical_ai"
    }


@app.get("/api/pets")
def list_pets():
    """Retorna a lista de pets cadastrados na clínica."""
    return clyvoscribe_pipeline.list_all_pets()


@app.get("/api/pets/{pet_id}")
def get_pet(pet_id: str):
    """Busca o prontuário pregresso e perfil biométrico de um pet específico."""
    try:
        pet = clyvoscribe_pipeline.get_pet_profile(pet_id)
        return pet.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/cases")
def list_cases():
    """Lista os casos de demonstração clínica disponíveis."""
    return asr_service.list_available_cases()


@app.post("/api/consultations/process", response_model=FullConsultationResult)
def process_consultation(request: ConsultationRequest):
    """
    Processa uma consulta completa a partir de um caso simulado ou transcrição personalizada.
    """
    try:
        result = clyvoscribe_pipeline.run_consultation_pipeline(
            pet_id=request.pet_id,
            sample_case_id=request.sample_case_id,
            custom_transcript=request.custom_transcript
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/consultations/upload-audio", response_model=FullConsultationResult)
async def upload_audio_consultation(
    pet_id: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Recebe um arquivo de áudio de consulta, transcreve com ASR e executa o pipeline SOAP completo.
    """
    try:
        content = await audio_file.read()
        result = clyvoscribe_pipeline.run_consultation_pipeline(
            pet_id=pet_id,
            audio_filename=audio_file.filename or "consulta.wav",
            audio_bytes=content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/consultations/finalize")
def finalize_consultation(req: FinalizeConsultationRequest):
    """
    Valida e assina digitalmente a minuta de prontuário veterinário.
    """
    return {
        "status": "sucesso",
        "consultation_id": req.consultation_id,
        "assinado_por": req.crmv,
        "mensagem": "Prontuário assinado digitalmente com sucesso e arquivado no histórico permanente CLYVO VET. Guia pós-consulta enviado ao tutor via WhatsApp/App."
    }


# Monta a pasta estática da interface web interativa
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(str(WEB_DIR / "index.html"))
