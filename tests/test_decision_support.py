"""
Testes unitários específicos para o motor determinístico de apoio à decisão (Symbolic AI).
"""
import unittest
from app.services.decision_support import decision_support_engine
from app.models.pet import PetHealthProfile, VaccineRecord
from app.models.consultation import (
    SOAPRecord, SubjectiveSection, ObjectiveSection, AssessmentSection,
    PlanSection, VitalSigns
)


class TestDecisionSupportEngine(unittest.TestCase):

    def setUp(self):
        self.mock_soap = SOAPRecord(
            subjective=SubjectiveSection(queixa_principal="Checkup", historico_molestia_atual="Sem queixas"),
            objective=ObjectiveSection(exame_fisico_geral="Normal", exame_fisico_especifico="Normal"),
            assessment=AssessmentSection(hipoteses_diagnosticas=["Avaliação de rotina"]),
            plan=PlanSection(exames_solicitados=[], prescricoes_farmacologicas=[])
        )

    def test_collie_mdr1_alert(self):
        pet = PetHealthProfile(
            pet_id="TEST-1",
            nome="Lassie",
            especie="canina",
            raca="Rough Collie",
            sexo="femea",
            idade_anos=4.0,
            peso_atual_kg=22.0
        )
        alerts = decision_support_engine.evaluate_safety_and_recommendations(
            pet, self.mock_soap, "O tutor perguntou se podia dar ivermectina para sarna"
        )
        alert_msgs = [a.mensagem for a in alerts]
        self.assertTrue(any("MDR1" in m for m in alert_msgs))
        self.assertTrue(any("neurotoxicidade" in m.lower() for m in alert_msgs))

    def test_feline_renal_nsaid_contraindication(self):
        pet = PetHealthProfile(
            pet_id="TEST-2",
            nome="Mimi",
            especie="felina",
            raca="Siamês",
            sexo="femea",
            idade_anos=12.0,
            peso_atual_kg=3.5,
            comorbidades_cronicas=["insuficiencia_renal_cronica"]
        )
        alerts = decision_support_engine.evaluate_safety_and_recommendations(
            pet, self.mock_soap, "Veterinário considerou meloxicam para analgesia"
        )
        critical_alerts = [a for a in alerts if a.nivel == "perigo_vermelho"]
        self.assertGreater(len(critical_alerts), 0)
        self.assertIn("nefrotóxico", critical_alerts[0].fator_desencadeante.lower())

    def test_vaccine_overdue_alert(self):
        pet = PetHealthProfile(
            pet_id="TEST-3",
            nome="Bidu",
            especie="canina",
            raca="SRD",
            sexo="macho",
            idade_anos=2.0,
            peso_atual_kg=10.0,
            historico_vacinal=[
                VaccineRecord(vacina="Antirrábica", data_aplicacao="2024-01-01", status="atrasada")
            ]
        )
        alerts = decision_support_engine.evaluate_safety_and_recommendations(pet, self.mock_soap, "Consulta simples")
        vac_alerts = [a for a in alerts if a.tipo == "vacina_pendente"]
        self.assertEqual(len(vac_alerts), 1)


if __name__ == "__main__":
    unittest.main()
