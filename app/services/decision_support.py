import unicodedata
from typing import List
from app.models.pet import PetHealthProfile
from app.models.consultation import SOAPRecord, ClinicalAlert


class DecisionSupportEngine:
    """
    Guardião de segurança clínica determinística (Symbolic AI).
    Não depende de probabilidades estocásticas de LLM, garantindo 100% de confiabilidade.
    """

    HERDING_BREEDS = [
        "border collie", "collie", "pastor australiano", "pastor de shetland",
        "pastor alemao", "old english sheepdog"
    ]

    BRACHYCEPHALIC_BREEDS = [
        "buldogue frances", "buldogue ingles", "pug", "shih tzu",
        "boston terrier", "lhasa apso", "pequines"
    ]

    MDR1_CONTRAINDICATED_DRUGS = [
        "ivermectina", "loperamida", "moxidectina", "doxorrubicina",
        "vinblastina", "vincristina"
    ]

    FELINE_NEPHROTOXIC_DRUGS = [
        "meloxicam", "cetoprofeno", "carprofeno", "ibuprofeno",
        "flunixir", "gentamicina", "amicacina"
    ]

    @staticmethod
    def _normalize(text: str) -> str:
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", text.lower())
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    def evaluate_safety_and_recommendations(
        self,
        pet: PetHealthProfile,
        soap: SOAPRecord,
        transcript: str
    ) -> List[ClinicalAlert]:
        alerts: List[ClinicalAlert] = []
        text_lower = self._normalize(transcript + " " + json_dump_soap(soap))
        raca_norm = self._normalize(pet.raca)

        # 1. Alerta Genético de Mutação MDR1 / ABCB1 (Raças Pastoras)
        if any(self._normalize(b) in raca_norm for b in self.HERDING_BREEDS):
            alerts.append(ClinicalAlert(
                tipo="seguranca_racial",
                nivel="alerta_amarelo",
                mensagem=f"Raça {pet.raca} possui alta incidência de mutação no gene MDR1 (Glicoproteína-P). Atenção redobrada com ivermectina, loperamida e quimioterápicos.",
                fator_desencadeante=f"Raça pastora: {pet.raca}"
            ))
            # Se o texto mencionar algum fármaco de risco
            for drug in self.MDR1_CONTRAINDICATED_DRUGS:
                if self._normalize(drug) in text_lower:
                    alerts.append(ClinicalAlert(
                        tipo="contraindicacao_farmacologica",
                        nivel="perigo_vermelho",
                        mensagem=f"ALERTA CRÍTICO: Menção ao fármaco '{drug.capitalize()}' em paciente da raça {pet.raca}. Risco severo de neurotoxicidade por deficiência de barreira hematoencefálica (gene MDR1). Fármaco contraindicado!",
                        fator_desencadeante=f"Prescrição/menção de {drug} em {pet.raca}"
                    ))

        # 2. Alerta de Síndrome Braquicefálica
        if any(self._normalize(b) in raca_norm for b in self.BRACHYCEPHALIC_BREEDS):
            alerts.append(ClinicalAlert(
                tipo="seguranca_racial",
                nivel="info",
                mensagem=f"Paciente braquicefálico ({pet.raca}). Estenose natural de narinas e condutos auditivos. Evitar contenção estressante e monitorar temperatura corporal para prevenir hipertermia/colapso respiratório.",
                fator_desencadeante=f"Fenótipo braquicefálico: {pet.raca}"
            ))

        # 3. Alerta Renal Felino (DRC x AINEs)
        if pet.especie.lower() == "felina":
            tem_drc = any("renal" in c.lower() for c in pet.comorbidades_cronicas)
            if tem_drc or "renal" in text_lower or soap.assessment.nivel_gravidade == "urgencia_imediata":
                for drug in self.FELINE_NEPHROTOXIC_DRUGS:
                    if drug in text_lower:
                        alerts.append(ClinicalAlert(
                            tipo="contraindicacao_farmacologica",
                            nivel="perigo_vermelho",
                            mensagem=f"CONTRAINDICAÇÃO ABSOLUTA: Anti-inflamatório '{drug.capitalize()}' mencionado para felino com comprometimento renal. Risco de precipitação de insuficiência renal aguda terminal.",
                            fator_desencadeante=f"Fármaco nefrotóxico ({drug}) em felino com histórico de DRC"
                        ))

        # 4. Alerta de Vacinação Atrasada
        for vac in pet.historico_vacinal:
            if vac.status == "atrasada":
                alerts.append(ClinicalAlert(
                    tipo="vacina_pendente",
                    nivel="alerta_amarelo",
                    mensagem=f"Imunização pendente: Vacina '{vac.vacina}' está atrasada (última dose em {vac.data_aplicacao}). Sugerir agendamento de reforço pós-cura clínica.",
                    fator_desencadeante=f"Vacina {vac.vacina} vencida"
                ))

        # 5. Alerta de Gravidade Imediata
        if soap.assessment.nivel_gravidade == "urgencia_imediata":
            alerts.append(ClinicalAlert(
                tipo="alerta_gravidade",
                nivel="perigo_vermelho",
                mensagem="Paciente classificado com GRAVIDADE IMEDIATA. Requer internamento para suporte intensivo/fluidoterapia e monitorização contínua de parâmetros vitais.",
                fator_desencadeante="Classificação clínica de urgência"
            ))

        return alerts


def json_dump_soap(soap: SOAPRecord) -> str:
    try:
        return soap.model_dump_json()
    except Exception:
        return ""


decision_support_engine = DecisionSupportEngine()
