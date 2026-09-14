"""
Modelos de dados do Pet, Perfil Biométrico e Histórico Médico (CLYVO VET).
"""
from typing import List, Optional
from app.models.base import BaseModel, Field


class VaccineRecord(BaseModel):
    vacina: str = ""
    data_aplicacao: str = ""
    status: str = "em_dia"


class ContinuousMedication(BaseModel):
    medicamento: str = ""
    frequencia: str = ""
    motivo: Optional[str] = None


class PetHealthProfile(BaseModel):
    pet_id: str = ""
    nome: str = ""
    especie: str = "canina"
    raca: str = ""
    sexo: str = "macho"
    castrado: bool = True
    idade_anos: float = 1.0
    peso_atual_kg: float = 10.0
    escore_corporal: str = "ideal"
    alergias_conhecidas: List[str] = []
    comorbidades_cronicas: List[str] = []
    historico_vacinal: List[VaccineRecord] = []
    medicamentos_continuos: List[ContinuousMedication] = []
    tutor_nome: str = "Tutor Responsável"
    tutor_telefone: str = "(11) 99999-9999"

    def __init__(self, **kwargs):
        # Converte sub-objetos se vierem como dicionários
        if "historico_vacinal" in kwargs:
            raw_vax = kwargs["historico_vacinal"]
            kwargs["historico_vacinal"] = [v if isinstance(v, VaccineRecord) else VaccineRecord(**v) for v in raw_vax]
        if "medicamentos_continuos" in kwargs:
            raw_meds = kwargs["medicamentos_continuos"]
            kwargs["medicamentos_continuos"] = [m if isinstance(m, ContinuousMedication) else ContinuousMedication(**m) for m in raw_meds]
        super().__init__(**kwargs)
