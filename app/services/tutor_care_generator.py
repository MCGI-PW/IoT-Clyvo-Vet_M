"""
Gerador de Comunicação Pós-Consulta para o Tutor e Motor de Recomendações Comerciais da Clínica.
Transforma dados clínicos técnicos em linguagem acolhedora para o tutor e oportunidades para a clínica.
"""
from typing import List
from app.models.pet import PetHealthProfile
from app.models.consultation import (
    SOAPRecord, TutorCareGuide, TutorMedicationSchedule,
    ClinicRecommendation, ClinicBillingItem
)


class TutorCareGenerator:
    """
    Gera mensagens personalizadas em linguagem leiga para o tutor (estilo WhatsApp).
    """

    def generate(self, pet: PetHealthProfile, soap: SOAPRecord) -> TutorCareGuide:
        saudacao = f"Olá, {pet.tutor_nome}! Aqui está o resumo com muito carinho dos cuidados para o(a) {pet.nome} após a consulta de hoje."
        
        # Resumo compreensível da condição
        diagnosticos = soap.assessment.hipoteses_diagnosticas
        resumo_doenca = " ".join(diagnosticos)
        if "otite" in resumo_doenca.lower():
            o_que_tem = f"O {pet.nome} está com uma infecção e inflamação nos ouvidos (otite), que está causando coceira, dor e secreção. Também notamos um início de irritação nas patinhas por lambedura."
            sinais_alerta = [
                f"{pet.nome} chorar muito ou ficar com a cabeça caída de lado continuamente.",
                "Surgimento de secreção com sangue ou pus espesso nos ouvidos.",
                "Inchaço na face ou recusa total de água e comida."
            ]
        elif "renal" in resumo_doenca.lower() or "urêmica" in resumo_doenca.lower():
            o_que_tem = f"A {pet.nome} teve uma piora no quadro renal, o que causou desidratação e os vômitos. Ela precisou de medicação na veia e internação preventiva para reidratar e proteger os rins."
            sinais_alerta = [
                "Persistência de vômitos mesmo após a medicação.",
                "Não urinar na caixinha de areia por mais de 12 horas seguidas.",
                "Ficar muito prostrada, fria ou com dificuldade para respirar."
            ]
        else:
            o_que_tem = f"O {pet.nome} teve um desconforto articular/muscular na patinha traseira após a corrida. Não há fratura óssea, mas requer repouso e anti-inflamatório apropriado."
            sinais_alerta = [
                f"{pet.nome} não conseguir apoiar a pata de forma alguma após 48 horas.",
                "Presença de inchaço visível ou calor excessivo no joelho.",
                "Apatia extrema ou febre."
            ]

        # Cronograma de remédios
        cronograma: List[TutorMedicationSchedule] = []
        for presc in soap.plan.prescricoes_farmacologicas:
            nome = presc.nome_comercial or presc.principio_ativo
            if presc.frequencia_horas == 12:
                horarios = ["08:00 da manhã", "20:00 da noite"]
            elif presc.frequencia_horas == 8:
                horarios = ["07:00 da manhã", "15:00 da tarde", "23:00 da noite"]
            elif presc.frequencia_horas == 24:
                horarios = ["09:00 da manhã (1x ao dia)"]
            else:
                horarios = [f"A cada {presc.frequencia_horas} horas"]

            instrucao = presc.instrucoes_especiais or f"Administrar {presc.dosagem} por via {presc.via}."

            cronograma.append(TutorMedicationSchedule(
                remedio=f"{nome} ({presc.forma_farmaceutica})",
                como_dar=f"{presc.dosagem} - {instrucao}",
                horarios_sugeridos=horarios,
                duracao=f"Seguir rigorosamente por {presc.duracao_dias} dias!"
            ))

        proximo = f"Retorno agendado na clínica para daqui a {soap.plan.retorno_agendado_dias or 10} dias para reavaliação. Qualquer urgência, chame a equipe da CLYVO VET!"

        return TutorCareGuide(
            saudacao=saudacao,
            o_que_o_pet_tem=o_que_tem,
            cronograma_medicamentos=cronograma,
            sinais_de_alerta=sinais_alerta,
            proximo_passo=proximo
        )


class ClinicRevenueRecommender:
    """
    Identifica oportunidades de faturamento de serviços mencionados e fidelização contínua.
    """

    PRICING_CATALOG = {
        "citologia": ("Citologia Diagnóstica Otológica/Cutânea", "exame", 85.00),
        "ultrassonografia": ("Ultrassonografia Abdominal Veterinária", "exame", 220.00),
        "fluidoterapia": ("Diária de Internação com Fluidoterapia Contínua", "procedimento", 320.00),
        "bioquímico": ("Painel Bioquímico Renal e Eletrólitos", "exame", 140.00),
        "radiografia": ("Estudo Radiográfico Digital (2 projeções)", "exame", 190.00),
        "vacina": ("Vacina Antirrábica / Polivalente de Reforço", "procedimento", 110.00),
        "retorno": ("Consulta de Retorno e Reavaliação", "retorno", 0.00),
    }

    def recommend(self, pet: PetHealthProfile, soap: SOAPRecord) -> ClinicRecommendation:
        itens: List[ClinicBillingItem] = []
        total = 0.0

        combined_text = (
            " ".join(soap.plan.exames_solicitados) + " " +
            " ".join(soap.plan.recomendacoes_manejo)
        ).lower()

        # Checa exames e procedimentos no plano
        for key, (nome_item, cat, valor) in self.PRICING_CATALOG.items():
            if key in combined_text:
                itens.append(ClinicBillingItem(
                    item=nome_item,
                    categoria=cat,
                    valor_estimado_reais=valor,
                    justificativa_clinica=f"Identificado a partir das solicitações clínicas da consulta para {pet.nome}."
                ))
                total += valor

        # Checa vacina pendente no cadastro do pet
        for vac in pet.historico_vacinal:
            if vac.status == "atrasada":
                valor_vac = 110.00
                itens.append(ClinicBillingItem(
                    item=f"Reforço de {vac.vacina}",
                    categoria="procedimento",
                    valor_estimado_reais=valor_vac,
                    justificativa_clinica=f"Vacina atrasada identificada pela IA no prontuário longitudinal do paciente."
                ))
                total += valor_vac

        # Ações de fidelização
        acoes = [
            f"Disparo automático de mensagem de check-in via WhatsApp para o tutor {pet.tutor_nome} em 48 horas.",
            f"Reserva automática de horário para o retorno presencial em {soap.plan.retorno_agendado_dias or 10} dias na agenda da clínica.",
            "Lembrete inteligente de recompra de ração ou medicamento de uso contínuo."
        ]

        return ClinicRecommendation(
            itens_faturaveis_sugeridos=itens,
            valor_total_potencial_reais=round(total, 2),
            acoes_de_fidelizacao=acoes
        )


tutor_care_generator = TutorCareGenerator()
clinic_recommender = ClinicRevenueRecommender()
