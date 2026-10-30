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
        demo_case = False
        if custom_transcript and custom_transcript.strip():
            transcript = custom_transcript.strip()
        elif sample_case_id:
            case_data = asr_service.get_case_by_id(sample_case_id)
            transcript = case_data.get("transcript", "")
            demo_case = True
        elif audio_bytes and audio_filename:
            transcript = asr_service.transcribe_audio_file(audio_filename, audio_bytes)
        else:
            # Fallback para caso padrão do pet
            sample_id = "CASE-MEL-RENAL" if pet.especie == "felina" else "CASE-THOR-OTITE"
            transcript = asr_service.get_case_by_id(sample_id).get("transcript", "")
            demo_case = True

        # 2. Extração do Prontuário Clínico SOAP
        soap_record = clinical_nlp_service.extract_soap_record(transcript, pet, demo_case=demo_case)

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


    def summarize_transcript(self, transcript: str, contexto_paciente: Optional[str] = None) -> Dict[str, Any]:
        """
        Resumo enxuto para integração com outros sistemas (ex.: API Java da CLYVO VET).
        Recebe só a transcrição e "Nome (Raça)" do pet: nenhum dado do tutor é necessário.
        """
        if not transcript or not transcript.strip():
            raise ValueError("A transcrição da consulta está vazia.")

        nome, raca = (contexto_paciente or "Pet").strip(), ""
        if "(" in nome and nome.endswith(")"):
            nome, raca = nome[:-1].split("(", 1)
            nome, raca = nome.strip(), raca.strip()
        pet = PetHealthProfile(pet_id="EXTERNO", nome=nome or "Pet", raca=raca,
                               especie="felina" if "gat" in raca.lower() else "canina")

        texto = transcript.strip()
        soap = clinical_nlp_service.extract_soap_record(texto, pet)
        alertas = decision_support_engine.evaluate_safety_and_recommendations(pet, soap, texto)
        guia = tutor_care_generator.generate(pet, soap)

        orientacoes = list(soap.plan.recomendacoes_manejo) + [f"Exame: {e}" for e in soap.plan.exames_solicitados]
        if soap.plan.retorno_agendado_dias and not any("retorn" in o.lower() for o in orientacoes):
            orientacoes.append(f"Retorno em {soap.plan.retorno_agendado_dias} dias.")

        return {
            "diagnostico": "; ".join(soap.assessment.hipoteses_diagnosticas),
            "prescricao": "\n".join(self._linha_prescricao(rx) for rx in soap.plan.prescricoes_farmacologicas),
            "orientacoes": "\n".join(orientacoes),
            "resumo_tutor": guia.o_que_o_pet_tem,
            "sinais_alerta": list(guia.sinais_de_alerta),
            "alertas_clinicos": [a.mensagem for a in alertas],
            "fonte": soap.fonte_ia,
        }

    @staticmethod
    def _linha_prescricao(rx) -> str:
        partes = [rx.nome_comercial or rx.principio_ativo]
        if rx.dosagem and rx.dosagem != rx.principio_ativo:
            partes.append(rx.dosagem)
        if rx.frequencia_horas:
            partes.append(f"a cada {rx.frequencia_horas}h")
        if rx.duracao_dias:
            partes.append(f"por {rx.duracao_dias} dias")
        return " — ".join(partes)


clyvoscribe_pipeline = ClyvoScribePipeline()
