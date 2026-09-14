"""
Orquestrador central do pipeline de IA da CLYVO VET (ClyvoScribe AI).
Conecta ASR -> NLP Clínico SOAP -> Apoio à Decisão -> Guia do Tutor & Recomendações da Clínica.
"""
import time
import json
import logging
from typing import Optional, Dict, Any
from app.config import SAMPLES_DIR, DEFAULT_VET_CRMV
from app.models.pet import PetHealthProfile
from app.models.consultation import FullConsultationResult
from app.services.asr_service import asr_service
from app.services.clinical_nlp import clinical_nlp_service
from app.services.decision_support import decision_support_engine
from app.services.tutor_care_generator import tutor_care_generator, clinic_recommender

logger = logging.getLogger(__name__)


class ClyvoScribePipeline:
    def __init__(self):
        self._pets_cache: Dict[str, PetHealthProfile] = {}
        self._load_pet_database()

    def _load_pet_database(self):
        pets_file = SAMPLES_DIR / "pet_profiles.json"
        if pets_file.exists():
            with open(pets_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for pid, pdata in raw_data.items():
                    self._pets_cache[pid] = PetHealthProfile(**pdata)

    def get_pet_profile(self, pet_id: str) -> PetHealthProfile:
        if pet_id in self._pets_cache:
            return self._pets_cache[pet_id]
        raise ValueError(f"Pet com identificador '{pet_id}' não localizado na base CLYVO VET.")

    def list_all_pets(self):
        return [p.model_dump() for p in self._pets_cache.values()]

    def run_consultation_pipeline(
        self,
        pet_id: str,
        sample_case_id: Optional[str] = None,
        custom_transcript: Optional[str] = None,
        audio_filename: Optional[str] = None,
        audio_bytes: Optional[bytes] = None
    ) -> FullConsultationResult:
        start_time = time.time()
        pet = self.get_pet_profile(pet_id)

        # 1. Obtenção da Transcrição via ASR ou Amostra
        if sample_case_id:
            case_data = asr_service.get_case_by_id(sample_case_id)
            transcript = case_data.get("transcript", "")
        elif audio_bytes and audio_filename:
            transcript = asr_service.transcribe_audio_file(audio_filename, audio_bytes)
        elif custom_transcript:
            transcript = custom_transcript.strip()
        else:
            # Fallback para caso padrão do pet
            sample_id = "CASE-MEL-RENAL" if pet.especie == "felina" else "CASE-THOR-OTITE"
            transcript = asr_service.get_case_by_id(sample_id).get("transcript", "")

        # 2. Extração do Prontuário Clínico SOAP
        soap_record = clinical_nlp_service.extract_soap_record(transcript, pet)

        # 3. Análise de Alertas e Segurança Clínica (Decision Support)
        clinical_alerts = decision_support_engine.evaluate_safety_and_recommendations(pet, soap_record, transcript)

        # 4. Geração do Guia de Cuidados do Tutor
        tutor_guide = tutor_care_generator.generate(pet, soap_record)

        # 5. Geração de Recomendações e Oportunidades para a Clínica
        clinic_rec = clinic_recommender.recommend(pet, soap_record)

        elapsed = round(time.time() - start_time, 2)
        consultation_id = f"CONS-{pet.pet_id}-{int(time.time())}"

        return FullConsultationResult(
            consultation_id=consultation_id,
            pet=pet,
            raw_transcript=transcript,
            soap=soap_record,
            alerts=clinical_alerts,
            tutor_guide=tutor_guide,
            clinic_recommendations=clinic_rec,
            tempo_processamento_segundos=elapsed,
            veterinario_crmv=DEFAULT_VET_CRMV,
            status="minuta_gerada_aguardando_assinatura"
        )


clyvoscribe_pipeline = ClyvoScribePipeline()
