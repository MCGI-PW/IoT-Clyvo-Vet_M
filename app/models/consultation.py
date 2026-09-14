"""
Modelos de dados para Consulta, Prontuário SOAP, Alertas Clínicos e Guias (CLYVO VET).
"""
from typing import List, Optional
from app.models.base import BaseModel, Field
from app.models.pet import PetHealthProfile


class VitalSigns(BaseModel):
    temperatura_retal_c: Optional[float] = None
    frequencia_cardiaca_bpm: Optional[int] = None
    frequencia_respiratoria_mpm: Optional[int] = None
    tempo_preenchimento_capilar_seg: Optional[int] = None
    grau_desidratacao_pct: Optional[int] = 0


class SubjectiveSection(BaseModel):
    queixa_principal: str = ""
    historico_molestia_atual: str = ""
    alimentacao_e_apetite: Optional[str] = None
    comportamento_e_rotina: Optional[str] = None


class ObjectiveSection(BaseModel):
    parametros_vitais: VitalSigns = None
    exame_fisico_geral: str = ""
    exame_fisico_especifico: str = ""

    def __init__(self, **kwargs):
        if "parametros_vitais" in kwargs:
            pv = kwargs["parametros_vitais"]
            kwargs["parametros_vitais"] = pv if isinstance(pv, VitalSigns) else VitalSigns(**pv)
        else:
            kwargs["parametros_vitais"] = VitalSigns()
        super().__init__(**kwargs)


class AssessmentSection(BaseModel):
    hipoteses_diagnosticas: List[str] = []
    nivel_gravidade: str = "monitoramento_moderado"


class PrescriptionItem(BaseModel):
    principio_ativo: str = ""
    nome_comercial: Optional[str] = None
    forma_farmaceutica: str = ""
    dosagem: str = ""
    frequencia_horas: int = 12
    duracao_dias: int = 7
    via: str = "Oral"
    instrucoes_especiais: Optional[str] = None


class PlanSection(BaseModel):
    exames_solicitados: List[str] = []
    prescricoes_farmacologicas: List[PrescriptionItem] = []
    recomendacoes_manejo: List[str] = []
    retorno_agendado_dias: Optional[int] = 10

    def __init__(self, **kwargs):
        if "prescricoes_farmacologicas" in kwargs:
            raw_rx = kwargs["prescricoes_farmacologicas"]
            kwargs["prescricoes_farmacologicas"] = [r if isinstance(r, PrescriptionItem) else PrescriptionItem(**r) for r in raw_rx]
        super().__init__(**kwargs)


class SOAPRecord(BaseModel):
    subjective: SubjectiveSection = None
    objective: ObjectiveSection = None
    assessment: AssessmentSection = None
    plan: PlanSection = None

    def __init__(self, **kwargs):
        if "subjective" in kwargs:
            s = kwargs["subjective"]
            kwargs["subjective"] = s if isinstance(s, SubjectiveSection) else SubjectiveSection(**s)
        if "objective" in kwargs:
            o = kwargs["objective"]
            kwargs["objective"] = o if isinstance(o, ObjectiveSection) else ObjectiveSection(**o)
        if "assessment" in kwargs:
            a = kwargs["assessment"]
            kwargs["assessment"] = a if isinstance(a, AssessmentSection) else AssessmentSection(**a)
        if "plan" in kwargs:
            p = kwargs["plan"]
            kwargs["plan"] = p if isinstance(p, PlanSection) else PlanSection(**p)
        super().__init__(**kwargs)


class ClinicalAlert(BaseModel):
    tipo: str = "seguranca_racial"
    nivel: str = "info"
    mensagem: str = ""
    fator_desencadeante: str = ""


class TutorMedicationSchedule(BaseModel):
    remedio: str = ""
    como_dar: str = ""
    horarios_sugeridos: List[str] = []
    duracao: str = ""


class TutorCareGuide(BaseModel):
    saudacao: str = ""
    o_que_o_pet_tem: str = ""
    cronograma_medicamentos: List[TutorMedicationSchedule] = []
    sinais_de_alerta: List[str] = []
    proximo_passo: str = ""

    def __init__(self, **kwargs):
        if "cronograma_medicamentos" in kwargs:
            raw_cm = kwargs["cronograma_medicamentos"]
            kwargs["cronograma_medicamentos"] = [c if isinstance(c, TutorMedicationSchedule) else TutorMedicationSchedule(**c) for c in raw_cm]
        super().__init__(**kwargs)


class ClinicBillingItem(BaseModel):
    item: str = ""
    categoria: str = "exame"
    valor_estimado_reais: float = 0.0
    justificativa_clinica: str = ""


class ClinicRecommendation(BaseModel):
    itens_faturaveis_sugeridos: List[ClinicBillingItem] = []
    valor_total_potencial_reais: float = 0.0
    acoes_de_fidelizacao: List[str] = []

    def __init__(self, **kwargs):
        if "itens_faturaveis_sugeridos" in kwargs:
            raw_ib = kwargs["itens_faturaveis_sugeridos"]
            kwargs["itens_faturaveis_sugeridos"] = [i if isinstance(i, ClinicBillingItem) else ClinicBillingItem(**i) for i in raw_ib]
        super().__init__(**kwargs)


class FullConsultationResult(BaseModel):
    consultation_id: str = ""
    pet: PetHealthProfile = None
    raw_transcript: str = ""
    soap: SOAPRecord = None
    alerts: List[ClinicalAlert] = []
    tutor_guide: TutorCareGuide = None
    clinic_recommendations: ClinicRecommendation = None
    tempo_processamento_segundos: float = 0.0
    veterinario_crmv: str = "CRMV-SP 45.892"
    status: str = "minuta_gerada_aguardando_assinatura"

    def __init__(self, **kwargs):
        if "pet" in kwargs:
            p = kwargs["pet"]
            kwargs["pet"] = p if isinstance(p, PetHealthProfile) else PetHealthProfile(**p)
        if "soap" in kwargs:
            s = kwargs["soap"]
            kwargs["soap"] = s if isinstance(s, SOAPRecord) else SOAPRecord(**s)
        if "alerts" in kwargs:
            raw_a = kwargs["alerts"]
            kwargs["alerts"] = [a if isinstance(a, ClinicalAlert) else ClinicalAlert(**a) for a in raw_a]
        if "tutor_guide" in kwargs:
            tg = kwargs["tutor_guide"]
            kwargs["tutor_guide"] = tg if isinstance(tg, TutorCareGuide) else TutorCareGuide(**tg)
        if "clinic_recommendations" in kwargs:
            cr = kwargs["clinic_recommendations"]
            kwargs["clinic_recommendations"] = cr if isinstance(cr, ClinicRecommendation) else ClinicRecommendation(**cr)
        super().__init__(**kwargs)
