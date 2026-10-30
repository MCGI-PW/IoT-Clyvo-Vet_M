"""
Serviço de Reconhecimento Automático de Fala (ASR) especializado em Medicina Veterinária.

- Ao vivo: a transcrição acontece no navegador (Web Speech API), veja app/web/app.js.
- Arquivo de áudio gravado: Whisper (pacote opcional `openai-whisper`), rodando local.
- Casos de demonstração: transcrições de exemplo em samples/audio_transcripts.json.
"""
import json
import logging
import os
import tempfile
from typing import Dict, Any, List
from app.config import SAMPLES_DIR

logger = logging.getLogger(__name__)


class ASRService:
    def __init__(self):
        self._samples_cache: Dict[str, Any] = {}
        self._whisper_model = None
        self._load_samples()

    def _load_samples(self):
        transcript_file = SAMPLES_DIR / "audio_transcripts.json"
        if transcript_file.exists():
            with open(transcript_file, "r", encoding="utf-8") as f:
                self._samples_cache = json.load(f)

    def list_available_cases(self) -> List[Dict[str, Any]]:
        """Retorna os casos simulados disponíveis para teste e demonstração."""
        cases = []
        for case_id, data in self._samples_cache.items():
            cases.append({
                "case_id": case_id,
                "title": data.get("title", case_id),
                "pet_id": data.get("pet_id", ""),
                "audio_duration_seconds": data.get("audio_duration_seconds", 120),
            })
        return cases

    def get_case_by_id(self, case_id: str) -> Dict[str, Any]:
        """Retorna a transcrição e metadados de um caso de demonstração."""
        if case_id in self._samples_cache:
            return self._samples_cache[case_id]
        raise ValueError(f"Caso {case_id} não encontrado.")

    def transcribe_audio_file(self, filename: str, content: bytes) -> str:
        """Transcreve um arquivo de áudio de consulta gravada com o Whisper (local, em português)."""
        logger.info(f"Processando áudio: {filename}, tamanho={len(content)} bytes")
        try:
            import whisper
        except ImportError:
            raise RuntimeError(
                "Transcrição de arquivo requer o pacote opcional 'openai-whisper' (pip install openai-whisper). "
                "Sem ele, use a transcrição ao vivo do navegador ou cole o texto da consulta."
            )

        if self._whisper_model is None:
            self._whisper_model = whisper.load_model(os.getenv("WHISPER_MODEL", "base"))
        sufixo = os.path.splitext(filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(suffix=sufixo, delete=False) as tmp:
            tmp.write(content)
            caminho = tmp.name
        try:
            return self._whisper_model.transcribe(caminho, language="pt")["text"].strip()
        finally:
            os.remove(caminho)


asr_service = ASRService()
