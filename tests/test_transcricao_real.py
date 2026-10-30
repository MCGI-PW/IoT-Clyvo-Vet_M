"""
Testes da transcrição real: extrator local por regras, Claude (com cliente falso) e resumo para integração.
"""
import json
import unittest
from types import SimpleNamespace

from app.models.pet import PetHealthProfile
from app.services.clinical_nlp import ClinicalNLPService
from app.services.claude_extractor import ClaudeSoapExtractor
from app.services.local_extractor import extrair_soap, frequencia_em_horas, duracao_em_dias
from app.services.pipeline import clyvoscribe_pipeline

CONSULTA_LIVRE = (
    "Tutor: A Luna está com diarreia há dois dias e não quer comer. "
    "Veterinário: A temperatura está 39,5 graus. Suspeita de gastroenterite. "
    "Vou passar um probiótico, um sachê uma vez ao dia durante uma semana. "
    "Dieta leve com ração úmida e bastante água. Peço um hemograma. "
    "Se ela tiver sangue nas fezes, procure atendimento imediatamente. Retorno em 5 dias."
)
PET = PetHealthProfile(pet_id="TEST", nome="Luna", especie="felina", raca="Siamês")


class ClienteClaudeFalso:
    """Imita client.messages.create do SDK da Anthropic, sem chamar a internet."""

    def __init__(self, resposta=None, stop_reason="end_turn", erro=None):
        self.resposta, self.stop_reason, self.erro = resposta, stop_reason, erro
        self.chamadas = []
        self.messages = self

    def create(self, **kwargs):
        self.chamadas.append(kwargs)
        if self.erro:
            raise self.erro
        bloco = SimpleNamespace(type="text", text=json.dumps(self.resposta))
        return SimpleNamespace(stop_reason=self.stop_reason, content=[bloco])


SOAP_CLAUDE = {
    "subjective": {"queixa_principal": "Diarreia há dois dias", "historico_molestia_atual": "Sem apetite",
                   "alimentacao_e_apetite": None, "comportamento_e_rotina": None},
    "objective": {"parametros_vitais": {"temperatura_retal_c": 39.5, "frequencia_cardiaca_bpm": None,
                                        "frequencia_respiratoria_mpm": None, "tempo_preenchimento_capilar_seg": None,
                                        "grau_desidratacao_pct": None},
                  "exame_fisico_geral": "Febril", "exame_fisico_especifico": ""},
    "assessment": {"hipoteses_diagnosticas": ["Gastroenterite"], "nivel_gravidade": "monitoramento_moderado"},
    "plan": {"exames_solicitados": ["Hemograma"], "recomendacoes_manejo": ["Dieta leve"], "retorno_agendado_dias": 5,
             "prescricoes_farmacologicas": [{"principio_ativo": "Probiótico", "nome_comercial": None,
                                             "forma_farmaceutica": "Sachê", "dosagem": "1 sachê",
                                             "frequencia_horas": 24, "duracao_dias": 7, "via": "Oral",
                                             "instrucoes_especiais": None}]},
    "resumo_tutor": "A Luna está com uma inflamação no intestino.",
    "sinais_alerta": ["Sangue nas fezes"],
}


class TestExtratorLocal(unittest.TestCase):

    def test_consulta_livre_usa_so_o_que_foi_dito(self):
        soap = extrair_soap(CONSULTA_LIVRE, PET)

        self.assertEqual(soap.fonte_ia, "LOCAL:extracao")
        self.assertIn("gastroenterite", soap.assessment.hipoteses_diagnosticas[0])
        self.assertEqual(soap.objective.parametros_vitais.temperatura_retal_c, 39.5)
        self.assertIsNone(soap.objective.parametros_vitais.frequencia_cardiaca_bpm)

        rx = soap.plan.prescricoes_farmacologicas
        self.assertEqual(len(rx), 1)
        self.assertEqual((rx[0].frequencia_horas, rx[0].duracao_dias), (24, 7))
        self.assertEqual(soap.plan.retorno_agendado_dias, 5)
        self.assertTrue(any("hemograma" in e for e in soap.plan.exames_solicitados))
        self.assertTrue(any("sangue nas fezes" in s for s in soap.sinais_alerta))
        # Nada dos protocolos de demonstração pode vazar para uma consulta real
        self.assertNotIn("Otite", " ".join(soap.assessment.hipoteses_diagnosticas))

    def test_frequencia_e_duracao_em_texto_falado(self):
        self.assertEqual(frequencia_em_horas("3 gotas duas vezes ao dia"), 12)
        self.assertEqual(frequencia_em_horas("um comprimido a cada 8 horas"), 8)
        self.assertIsNone(frequencia_em_horas("aplicar a pomada"))
        self.assertEqual(duracao_em_dias("por sete dias"), 7)
        self.assertEqual(duracao_em_dias("durante duas semanas"), 14)

    def test_sem_retorno_falado_nao_inventa_prazo(self):
        result = clyvoscribe_pipeline.run_consultation_pipeline(
            pet_id="PET-8921", custom_transcript="Suspeita de alergia. Evite petiscos."
        )
        self.assertIsNone(result.soap.plan.retorno_agendado_dias)
        self.assertNotIn("10 dias", result.tutor_guide.proximo_passo)


class TestClaude(unittest.TestCase):

    def test_resposta_estruturada_vira_soap(self):
        cliente = ClienteClaudeFalso(resposta=SOAP_CLAUDE)
        nlp = ClinicalNLPService(llm=ClaudeSoapExtractor(model="claude-opus-5-5", client=cliente))

        soap = nlp.extract_soap_record(CONSULTA_LIVRE, PET)

        self.assertEqual(soap.fonte_ia, "CLAUDE:claude-opus-5-5")
        self.assertEqual(soap.assessment.hipoteses_diagnosticas, ["Gastroenterite"])
        self.assertEqual(soap.plan.prescricoes_farmacologicas[0].frequencia_horas, 24)
        chamada = cliente.chamadas[0]
        self.assertEqual(chamada["output_config"]["format"]["type"], "json_schema")
        # LGPD: o nome do tutor não vai para a IA
        self.assertNotIn(PET.tutor_nome, chamada["messages"][0]["content"])

    def test_falha_ou_recusa_do_claude_cai_no_extrator_local(self):
        for cliente in (ClienteClaudeFalso(erro=ConnectionError("sem rede")),
                        ClienteClaudeFalso(resposta=SOAP_CLAUDE, stop_reason="refusal")):
            nlp = ClinicalNLPService(llm=ClaudeSoapExtractor(client=cliente))
            soap = nlp.extract_soap_record(CONSULTA_LIVRE, PET)
            self.assertEqual(soap.fonte_ia, "LOCAL:extracao")


class TestResumoParaIntegracao(unittest.TestCase):

    def test_resumo_no_formato_da_api_java(self):
        resumo = clyvoscribe_pipeline.summarize_transcript(CONSULTA_LIVRE, "Luna (Siamês)")

        self.assertEqual(set(resumo), {"diagnostico", "prescricao", "orientacoes", "resumo_tutor",
                                       "sinais_alerta", "alertas_clinicos", "fonte"})
        self.assertIn("gastroenterite", resumo["diagnostico"])
        self.assertIn("a cada 24h", resumo["prescricao"])
        self.assertIn("Luna", resumo["resumo_tutor"])

    def test_transcricao_vazia_e_rejeitada(self):
        with self.assertRaises(ValueError):
            clyvoscribe_pipeline.summarize_transcript("   ")


if __name__ == "__main__":
    unittest.main()
