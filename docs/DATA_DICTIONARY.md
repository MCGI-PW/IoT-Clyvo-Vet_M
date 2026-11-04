# Dicionário de Dados: AuroraScribe AI (Aurora Pet)

Os schemas abaixo são os que o código usa: modelos em `app/models/` e contrato da integração em `app/services/pipeline.py`.

---

## 1. Ciclo de vida dos dados

1. **Captura:** a fala vira texto no navegador (Web Speech API), o áudio gravado vira texto no Whisper, ou o texto é colado.
2. **Enriquecimento:** a transcrição é combinada com o perfil do pet (espécie, raça, peso, comorbidades, vacinas).
3. **Inferência e validação:** o Claude (ou o extrator local) gera o SOAP, e as regras clínicas acrescentam os alertas.
4. **Armazenamento:** o AuroraScribe **não guarda nada**: processa e devolve. Quem grava é a API Java, no Oracle:
   - a sugestão da IA, na tabela `transcricao_consulta`;
   - o prontuário, na tabela `prontuario`, só quando o veterinário conclui o atendimento.

O áudio não é armazenado: a Web Speech API entrega só o texto, e o arquivo enviado ao Whisper é apagado logo após a transcrição.

---

## 2. Origem e uso de cada dado

| Entidade | Origem | Formato | Uso pela IA |
|---|---|---|---|
| Transcrição | Microfone, arquivo de áudio ou texto | Texto livre | Entrada do SOAP |
| Perfil do pet (`PetHealthProfile`) | Cadastro da Aurora Pet (na demonstração, `samples/pet_profiles.json`) | JSON | Regras de raça e espécie, dose por kg |
| Comorbidades e alergias | Prontuário do pet | Lista de textos | Contraindicações (ex.: felino renal) |
| Histórico vacinal | Cartão de vacinas | Lista de `{vacina, data_aplicacao, status}` | Alerta de vacina atrasada e sugestão de reforço |
| Prontuário SOAP (`SOAPRecord`) | Saída da IA | JSON | Minuta para o veterinário revisar |
| Alertas (`ClinicalAlert`) | Regras clínicas | JSON | Cards de segurança |
| Guia do tutor (`TutorCareGuide`) | Saída da IA | JSON | Resumo, horários e sinais de alerta |
| Sugestões da clínica (`ClinicRecommendation`) | Regras sobre o plano | JSON | Exames, retorno, vacinas e valor estimado |
| Casos de exemplo | `samples/audio_transcripts.json` | JSON | Demonstração e testes |

---

## 3. Contrato da integração com a API Java

### 3.1 Requisição: `POST /api/transcriptions/summarize`

```json
{
  "transcript": "Tutora: O Thor está coçando muito a orelha direita há três dias...\nVeterinário: Parece ser uma otite externa. Vou prescrever solução otológica, 3 gotas duas vezes ao dia por 7 dias...",
  "contexto_paciente": "Thor (Buldogue Francês)"
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|:---:|---|
| `transcript` | string | ✅ | Texto da consulta. Vazio responde HTTP 400. |
| `contexto_paciente` | string | — | `"Nome (Raça)"`. Raça com "gat" é tratada como felina. |

### 3.2 Resposta (saída real do extrator local para a consulta acima)

```json
{
  "diagnostico": "Parece ser uma otite externa.",
  "prescricao": "Solução otológica — 3 gotas — a cada 12h — por 7 dias",
  "orientacoes": "Mantenha a orelha seca e não use cotonete.\nRetorno em 10 dias.",
  "resumo_tutor": "Resumo da consulta do(a) Thor. O que o(a) veterinário(a) avaliou: Parece ser uma otite externa. Foram indicados 1 medicamento(s); siga os horários abaixo. Cuidados em casa: Mantenha a orelha seca e não use cotonete. Retorno em 10 dias.",
  "sinais_alerta": ["Se ele tiver febre ou parar de comer, volte antes."],
  "alertas_clinicos": ["Paciente braquicefálico (Buldogue Francês). Estenose natural de narinas e condutos auditivos. Evitar contenção estressante e monitorar temperatura corporal para prevenir hipertermia/colapso respiratório."],
  "fonte": "LOCAL:extracao"
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `diagnostico` | string | Hipóteses diagnósticas separadas por `; ` |
| `prescricao` | string | Uma linha por remédio: nome, dose, intervalo, duração |
| `orientacoes` | string | Cuidados em casa, exames e retorno, um por linha |
| `resumo_tutor` | string | Texto simples para o tutor |
| `sinais_alerta` | lista de strings | Quando voltar à clínica |
| `alertas_clinicos` | lista de strings | Alertas das regras clínicas (a API Java mostra com ⚠) |
| `fonte` | string | `CLAUDE:<modelo>` ou `LOCAL:extracao` |

### 3.3 Onde a API Java grava: tabela `transcricao_consulta` (Oracle, Flyway V7)

| Coluna | Tipo | Conteúdo |
|---|---|---|
| `id_transcricao` | RAW(16) | Chave primária |
| `id_consulta` | RAW(16) | FK para `consulta` |
| `texto_transcricao` | CLOB | Transcrição enviada |
| `diagnostico_sugerido` | VARCHAR2(4000) | `diagnostico` |
| `prescricao_sugerida` | VARCHAR2(4000) | `prescricao` |
| `orientacoes_sugeridas` | VARCHAR2(4000) | `orientacoes` |
| `resumo_tutor` | VARCHAR2(4000) | `resumo_tutor` |
| `sinais_alerta` | VARCHAR2(4000) | `sinais_alerta` + `alertas_clinicos`, um por linha |
| `fonte_ia` | VARCHAR2(30) | `AURORASCRIBE`, `CLAUDE:<modelo>` ou `LOCAL` |
| `data_geracao` | TIMESTAMP | Quando a sugestão foi gerada |

---

## 4. Modelos do pipeline completo

### 4.1 Perfil do pet (`PetHealthProfile`)
```json
{
  "pet_id": "PET-6734",
  "nome": "Bob",
  "especie": "canina",
  "raca": "Border Collie",
  "sexo": "macho",
  "castrado": false,
  "idade_anos": 5.0,
  "peso_atual_kg": 19.5,
  "escore_corporal": "ideal",
  "alergias_conhecidas": [],
  "comorbidades_cronicas": [],
  "historico_vacinal": [
    {"vacina": "V8 Polivalente", "data_aplicacao": "2025-02-15", "status": "em_dia"},
    {"vacina": "Antirrábica", "data_aplicacao": "2025-02-15", "status": "em_dia"}
  ],
  "medicamentos_continuos": [],
  "tutor_nome": "Fernanda Lima",
  "tutor_telefone": "(11) 99345-6789"
}
```
`tutor_nome` só aparece na saudação do guia na tela. `tutor_telefone` não é usado pela IA e nenhum dos dois vai para o Claude.

### 4.2 Prontuário (`SOAPRecord`)
```json
{
  "subjective": {
    "queixa_principal": "string",
    "historico_molestia_atual": "string",
    "alimentacao_e_apetite": "string | null",
    "comportamento_e_rotina": "string | null"
  },
  "objective": {
    "parametros_vitais": {
      "temperatura_retal_c": "number | null",
      "frequencia_cardiaca_bpm": "integer | null",
      "frequencia_respiratoria_mpm": "integer | null",
      "tempo_preenchimento_capilar_seg": "integer | null",
      "grau_desidratacao_pct": "integer | null"
    },
    "exame_fisico_geral": "string",
    "exame_fisico_especifico": "string"
  },
  "assessment": {
    "hipoteses_diagnosticas": ["string"],
    "nivel_gravidade": "rotina_estavel | monitoramento_moderado | urgencia_imediata"
  },
  "plan": {
    "exames_solicitados": ["string"],
    "prescricoes_farmacologicas": [{
      "principio_ativo": "string",
      "nome_comercial": "string | null",
      "forma_farmaceutica": "string",
      "dosagem": "string",
      "frequencia_horas": "integer | null",
      "duracao_dias": "integer | null",
      "via": "string",
      "instrucoes_especiais": "string | null"
    }],
    "recomendacoes_manejo": ["string"],
    "retorno_agendado_dias": "integer | null"
  },
  "resumo_tutor": "string | null",
  "sinais_alerta": ["string"],
  "fonte_ia": "CLAUDE:<modelo> | LOCAL:extracao | LOCAL:protocolo-demo"
}
```
É o mesmo formato do `SOAP_SCHEMA` enviado ao Claude (`app/services/claude_extractor.py`), menos `fonte_ia`, que o próprio serviço preenche.

### 4.3 Alerta clínico (`ClinicalAlert`)
```json
{
  "tipo": "seguranca_racial | contraindicacao_farmacologica | vacina_pendente | alerta_gravidade",
  "nivel": "info | alerta_amarelo | perigo_vermelho",
  "mensagem": "Raça Border Collie possui alta incidência de mutação no gene MDR1...",
  "fator_desencadeante": "Raça pastora: Border Collie"
}
```

### 4.4 Guia do tutor (`TutorCareGuide`)
```json
{
  "saudacao": "Olá, Fernanda Lima! Aqui está o resumo...",
  "o_que_o_pet_tem": "Texto simples sobre o quadro",
  "cronograma_medicamentos": [{
    "remedio": "Rimadyl / Carproflan (Comprimidos mastigáveis)",
    "como_dar": "4.0 mg/kg (78.0 mg ao dia) - Oferecer sempre logo após alimentação...",
    "horarios_sugeridos": ["09:00 da manhã (1x ao dia)"],
    "duracao": "Seguir rigorosamente por 5 dias!"
  }],
  "sinais_de_alerta": ["string"],
  "proximo_passo": "Retorno agendado na clínica para daqui a 7 dias..."
}
```
Os horários saem do intervalo: 12h → 08:00 e 20:00; 8h → 07:00, 15:00 e 23:00; 24h → 09:00.

### 4.5 Sugestões da clínica (`ClinicRecommendation`)
```json
{
  "itens_faturaveis_sugeridos": [{
    "item": "Estudo Radiográfico Digital (2 projeções)",
    "categoria": "exame",
    "valor_estimado_reais": 190.0,
    "justificativa_clinica": "Identificado a partir das solicitações clínicas da consulta para Bob."
  }],
  "valor_total_potencial_reais": 190.0,
  "acoes_de_fidelizacao": ["Sugestão: mensagem de acompanhamento para o tutor Fernanda Lima em 48 horas."]
}
```
Os valores vêm de uma tabela de preços de demonstração (`PRICING_CATALOG`).

### 4.6 Resultado completo (`FullConsultationResult`)
Resposta de `POST /api/consultations/process`: `consultation_id`, `pet`, `raw_transcript`, `soap`, `alerts`, `tutor_guide`, `clinic_recommendations`, `tempo_processamento_segundos`, `veterinario_crmv` e `status` (`minuta_gerada_aguardando_assinatura`).
