# Dicionário e Estrutura de Dados: ClyvoScribe AI (CLYVO VET)

## 1. Visão Geral do Ciclo de Vida dos Dados

A inteligência da solução depende da combinação entre **dados estáticos e históricos** (cadastrados no sistema da CLYVO VET) e **dados dinâmicos e temporais** (capturados oralmente durante o atendimento).

O ciclo de vida é estruturado em quatro fases:
1. **Ingestão**: Captura de metadados do paciente e gravação de áudio de alta fidelidade (16 kHz / 44.1 kHz, mono).
2. **Transformação e Enriquecimento**: Conversão de voz em texto, extração de entidades biomédicas (NER) e vinculação com o prontuário.
3. **Inferência e Validação**: Geração do SOAP pelo LLM e validação contra regras determinísticas de farmacovigilância.
4. **Armazenamento e Retenção**: Gravação do prontuário no PostgreSQL; retenção do áudio bruto sob política de 30 dias para auditoria (com exclusão programada para conformidade com a LGPD).

---

## 2. Matriz de Origem, Estrutura e Utilização dos Dados

| Entidade de Dados | Origem | Formato / Tipo | Utilização pela IA |
| :--- | :--- | :--- | :--- |
| **Perfil Biométrico do Pet** | Cadastro CLYVO VET | JSON / Objeto Estruturado | Cálculo de dosagens por peso (mg/kg), verificação de predisposição por espécie/raça (ex: mutação MDR1, síndrome braquicefálica). |
| **Histórico Clínico Pregresso** | Prontuário Eletrônico | Lista de Registros Clínicos | Identificação de doenças crônicas (ex: DRC, cardiopatias) e alertas de interações com medicações em uso contínuo. |
| **Cartão de Vacinas** | Módulo de Vacinação CLYVO VET | Lista cronológica com datas de aplicação e lote | Detecção de vacinas em atraso para recomendação proativa de imunização preventiva. |
| **Comportamento & Estilo de Vida** | Anamnese & App do Tutor | Tags categóricas e texto livre | Avaliação de risco ambiental (ex: animal com acesso à rua, convívio com outros pets, ingestão de ossos/corpos estranhos). |
| **Áudio da Consulta** | Microfone do Veterinário | Stream PCM / Opus (WAV/WebM) | Alimentação do modelo ASR para transcrição com diarização (separação de interlocutores). |
| **Prontuário SOAP** | Inferência do LLM | JSON padronizado Pydantic | Minuta oficial de consulta para assinatura do veterinário e arquivo legal. |
| **Guia do Tutor** | Inferência do LLM | Markdown / JSON | Mensagem empática em linguagem acessível contendo horários de remédios e sinais de alerta enviada ao tutor. |
| **Métricas da Clínica** | Motor de Recomendação | JSON | Lista de exames complementares sugeridos e datas de retorno para faturamento e gestão de lealdade. |

---

## 3. Especificação Detalhada dos Schemas (JSON / Pydantic)

### 3.1 Perfil do Pet e Histórico (`PetHealthProfile`)
```json
{
  "pet_id": "PET-8921",
  "nome": "Thor",
  "especie": "canina",
  "raca": "Buldogue Francês",
  "sexo": "macho",
  "castrado": true,
  "idade_anos": 3.5,
  "peso_atual_kg": 12.8,
  "escore_corporal": "sobrepeso_leve",
  "alergias_conhecidas": ["frango", "picada_de_pulga"],
  "comorbidades_cronicas": ["dermatite_atopica", "sindrome_braquicefalica"],
  "historico_vacinal": [
    {
      "vacina": "V10 Poliovalente",
      "data_aplicacao": "2025-08-10",
      "status": "em_dia"
    },
    {
      "vacina": "Antirrabica",
      "data_aplicacao": "2024-05-12",
      "status": "atrasada"
    }
  ],
  "medicamentos_continuos": [
    {
      "medicamento": "Apoquel 5.4mg",
      "frequencia": "1 comprimido a cada 24h"
    }
  ]
}
```

### 3.2 Prontuário Clínico Estruturado (`SOAPRecord`)
```json
{
  "consultation_id": "CONS-2026-0914-01",
  "pet_id": "PET-8921",
  "timestamp": "2026-09-14T10:30:00Z",
  "veterinario_crmv": "CRMV-SP 45.892",
  "soap": {
    "subjective": {
      "queixa_principal": "Prurido intenso nas orelhas e lambedura excessiva das patas há 4 dias.",
      "historico_molestia_atual": "Tutor relata que o animal começou a chacoalhar a cabeça com frequência após banho no final de semana. Odor fétido no conduto auditivo direito.",
      "alimentacao": "Ração hipoalergênica, porém tutor ofereceu petisco comercial não rotineiro."
    },
    "objective": {
      "parametros_vitais": {
        "temperatura_retal_c": 38.6,
        "frequencia_cardiaca_bpm": 110,
        "frequencia_respiratoria_mpm": 26,
        "tempo_preenchimento_capilar_seg": 2,
        "grau_desidratacao_pct": 0
      },
      "exame_fisico_geral": "Animal alerta, hidratado, mucosas normocoradas.",
      "exame_fisico_especifico": "Otoscopia: conduto auditivo bilateral eritematoso, com presença de exsudato ceruminoso castanho abundante e descamação no pavilhão auricular direito. Otalgia moderada à palpação."
    },
    "assessment": {
      "hipoteses_diagnosticas": [
        "Otite externa bilateral ceruminosa (provável etiologia por Malassezia pachydermatis)",
        "Agudização de dermatite atópica secundária a gatilho alimentar/ambiental"
      ],
      "nivel_gravidade": "monitoramento_moderado"
    },
    "plan": {
      "exames_solicitados": [
        "Citologia de cerúmen otológico bilateral",
        "Raspado de pele com fita adesiva (tape strip)"
      ],
      "prescricoes_farmacologicas": [
        {
          "principio_ativo": "Ciprofloxacina + Cetoconazol + Betametasona",
          "nome_comercial": "Aurivet ou Otomax",
          "forma_farmaceutica": "Gotas otológicas",
          "dosagem": "4 gotas em cada conduto",
          "frequencia_horas": 12,
          "duracao_dias": 10,
          "via": "topica_auricular",
          "instrucoes_especiais": "Realizar limpeza prévia com solução ceruminolítica antes da aplicação."
        }
      ],
      "recomendacoes_manejo": [
        "Evitar molhar os ouvidos durante banhos; usar algodão parafermentado.",
        "Suspender imediatamente qualquer petisco comercial fora da dieta prescrita."
      ],
      "retorno_agendado_dias": 10
    }
  }
}
```

### 3.3 Alertas de Segurança Clínica (`ClinicalAlert`)
```json
{
  "alertas": [
    {
      "tipo": "seguranca_racial",
      "nivel": "alerta_amarelo",
      "mensagem": "Buldogue Francês possui estenose natural de conduto auditivo e sensibilidade respiratória. Monitorar ventilação e evitar estresse excessivo durante limpeza profunda.",
      "fator_desencadeante": "raca: Buldogue Frances"
    },
    {
      "tipo": "vacina_pendente",
      "nivel": "preventivo",
      "mensagem": "Vacina Antirrábica vencida desde Maio/2025. Recomendado reforço vacinal assim que resolvido o quadro infeccioso auricular.",
      "fator_desencadeante": "vacina: Antirrabica atrasada"
    }
  ]
}
```

### 3.4 Guia de Cuidados para o Tutor (`TutorCareGuide`)
```json
{
  "saudacao": "Olá, tutor do Thor! Aqui está o resumo simplificado da consulta de hoje com Dr(a). Veterinário(a).",
  "o_que_o_thor_tem": "O Thor está com uma inflamação e infecção de ouvido (otite) que está fazendo ele coçar muito e chacoalhar a cabeça.",
  "cronograma_medicamentos": [
    {
      "remedio": "Aurivet (Gotas no Ouvido)",
      "como_dar": "Limpe o ouvidinho com a loção e pingue 4 gotinhas em cada ouvido.",
      "horarios_sugeridos": ["08:00", "20:00"],
      "duracao": "Fazer durante 10 dias sem interrupção!"
    }
  ],
  "sinais_de_alerta": [
    "Thor ficar com a cabeça caída de lado continuamente.",
    "Aparecimento de secreção com sangue ou pus no ouvido.",
    "Parar de comer ou ficar prostrado."
  ],
  "proximo_passo": "Retorno agendado para daqui a 10 dias para conferir se o ouvido sarou completamente."
}
```
