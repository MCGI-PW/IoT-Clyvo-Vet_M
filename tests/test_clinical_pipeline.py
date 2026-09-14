"""
Testes automatizados do pipeline de IA clínica da CLYVO VET (ClyvoScribe AI).
"""
import unittest
from app.services.pipeline import clyvoscribe_pipeline
from app.models.consultation import FullConsultationResult


class TestClinicalPipeline(unittest.TestCase):

    def test_pipeline_thor_otite(self):
        """Valida a extração e estruturação para o caso do cão Thor (Buldogue Francês)."""
        result = clyvoscribe_pipeline.run_consultation_pipeline(
            pet_id="PET-8921",
            sample_case_id="CASE-THOR-OTITE"
        )

        self.assertIsInstance(result, FullConsultationResult)
        self.assertEqual(result.pet.nome, "Thor")
        self.assertEqual(result.pet.raca, "Buldogue Francês")
        
        # Validação do SOAP
        self.assertIn("otite", result.soap.assessment.hipoteses_diagnosticas[0].lower())
        self.assertGreater(len(result.soap.plan.prescricoes_farmacologicas), 0)
        self.assertEqual(result.soap.plan.retorno_agendado_dias, 10)

        # Validação do Guia do Tutor
        self.assertIn("Thor", result.tutor_guide.saudacao)
        self.assertGreater(len(result.tutor_guide.cronograma_medicamentos), 0)

        # Validação de Alertas (Buldogue é braquicefálico e possui vacina antirrábica atrasada)
        alert_types = [a.tipo for a in result.alerts]
        self.assertIn("seguranca_racial", alert_types)
        self.assertIn("vacina_pendente", alert_types)

    def test_pipeline_mel_renal(self):
        """Valida a extração para o caso da gata Mel (Siamês geriátrica com DRC)."""
        result = clyvoscribe_pipeline.run_consultation_pipeline(
            pet_id="PET-4102",
            sample_case_id="CASE-MEL-RENAL"
        )

        self.assertEqual(result.pet.nome, "Mel")
        self.assertEqual(result.soap.assessment.nivel_gravidade, "urgencia_imediata")
        
        # Alerta de contraindicação renal por menção de meloxicam
        danger_alerts = [a for a in result.alerts if a.nivel == "perigo_vermelho"]
        self.assertGreater(len(danger_alerts), 0)

    def test_pipeline_bob_mdr1(self):
        """Valida a salvaguarda de mutação genética MDR1 para Border Collie."""
        result = clyvoscribe_pipeline.run_consultation_pipeline(
            pet_id="PET-6734",
            sample_case_id="CASE-BOB-COLLIE"
        )

        self.assertEqual(result.pet.nome, "Bob")
        # Deve conter alerta de segurança para raça pastora e contraindicação crítica por menção a ivermectina
        mdr1_alerts = [a for a in result.alerts if "mdr1" in a.mensagem.lower()]
        self.assertGreater(len(mdr1_alerts), 0)


if __name__ == "__main__":
    unittest.main()
