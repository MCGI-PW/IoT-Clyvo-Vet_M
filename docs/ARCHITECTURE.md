# Arquitetura Técnica do Sistema: ClyvoScribe AI (CLYVO VET)

## 1. Visão Geral da Arquitetura

O **ClyvoScribe AI** é concebido como um microsserviço inteligente de alta disponibilidade desacoplado da plataforma central **CLYVO VET**, comunicando-se via API RESTful e WebSockets para streaming de áudio e dados em tempo real.

A arquitetura adota o padrão **Clean Architecture** com separação explícita de responsabilidades:
- **Camada de Apresentação (Interface)**: Dashboard web e mobile para o Médico-Veterinário e aplicativo móvel / portal do Tutor.
- **Camada de Aplicação & Orquestração (API Gateway & Pipeline)**: Endpoints FastAPI com validação de tipos em Pydantic e fila assíncrona.
- **Camada de Inteligência Artificial (Inference Engine)**:
  - *ASR Engine*: Processamento de áudio acústico e conversão fonema-texto com diarização.
  - *Clinical NLP Engine*: Modelo generativo instruído para extração SOAP e estruturação de prescrições.
  - *Safety Guardrails*: Motor determinístico de regras de farmacovigilância e predisposição racial.
- **Camada de Persistência (Database & Cache)**: Banco relacional (PostgreSQL) para dados transacionais e prontuários; Redis para fila e cache de sessões ativas de áudio.

---

## 2. Diagrama Arquitetural de Componentes

```mermaid
graph TB
    subgraph Client_Layer ["Camada de Clientes"]
        VET_APP["App / Dashboard Veterinário (Web/Tablet)"]
        TUTOR_APP["App do Tutor / WhatsApp Integration"]
    end

    subgraph Gateway_Layer ["API Gateway & Ingestão"]
        FASTAPI["FastAPI Orchestrator / Reverse Proxy"]
        AUTH["Auth & Consent Module (LGPD)"]
    end

    subgraph AI_Layer ["Pipeline de Inteligência Artificial"]
        ASR["1. ASR Engine (Whisper / Gemini Multimodal)"]
        NLP["2. Clinical LLM (Structured SOAP Extractor)"]
        SAFETY["3. Decision Support & Safety Engine (Regras CFMV/MDR1)"]
        TUTOR_GEN["4. Tutor Care Generator (Plain Language + Schedule)"]
    end

    subgraph Data_Layer ["Camada de Persistência & Integração"]
        PG[("PostgreSQL: Prontuários, Pets, Consultas")]
        REDIS[("Redis: Sessões de Áudio em Andamento")]
        EHR_API["CLYVO VET Core EHR API"]
    end

    VET_APP -->|1. Stream de Áudio / Gravação| FASTAPI
    FASTAPI --> AUTH
    AUTH -->|Áudio Autenticado e Consentido| ASR
    ASR -->|Transcrição com Locutores| NLP
    EHR_API -->|Perfil do Pet, Histórico e Vacinas| NLP
    NLP -->|SOAP Preliminar| SAFETY
    SAFETY -->|SOAP Validado + Alertas Clínicos| PG
    SAFETY --> TUTOR_GEN
    TUTOR_GEN -->|Guia Amigável & Alarmes| PG
    PG -->|Notificação Push / Mensagem| TUTOR_APP
    PG -->|Prontuário Estruturado para Validação| VET_APP
```

---

## 3. Diagrama de Sequência e Fluxo de Dados Fim a Fim

O fluxo completo entre os usuários, a aplicação, os bancos de dados e os modelos de IA ocorre em seis etapas síncronas/assíncronas:

```mermaid
sequenceDiagram
    autonumber
    actor V as Médico-Veterinário
    actor T as Tutor do Pet
    participant App as Clyvo Vet Web/App
    participant API as Backend FastAPI
    participant DB as Banco de Dados (EHR)
    participant ASR as Módulo ASR (Áudio -> Texto)
    participant LLM as Módulo Clinical NLP (LLM)
    participant RuleEngine as Motor de Regras & Alertas

    V->>App: Inicia consulta (Pet: Thor, Buldogue Francês)
    App->>API: GET /api/pets/{id}/context
    API->>DB: Busca histórico, vacinas e alergias
    DB-->>API: Retorna perfil clínico
    API-->>App: Exibe painel pré-consulta com alertas preventivos

    V->>T: Solicita consentimento de gravação ambiental
    T-->>V: Autoriza gravação da consulta
    V->>App: Pressiona "Iniciar Escuta Inteligente"
    
    Note over V,T: Diálogo médico-veterinário e exame físico ocorrem naturalmente
    
    V->>App: Finaliza consulta ("Encerrar Escuta")
    App->>API: POST /api/consultations/process (Áudio ou Stream)
    API->>ASR: Envia arquivo de áudio
    ASR-->>API: Retorna Transcrição Integral com Diarização

    API->>LLM: Prompt Contextualizado (Transcrição + Histórico do Pet)
    LLM-->>API: Retorna JSON Estruturado (S-O-A-P + Fármacos + Exames)

    API->>RuleEngine: Valida Prescrição contra Regras Clínicas (Raça / Peso)
    RuleEngine-->>API: Anexa Alertas de Contraindicação (ex: Corticoide / MDR1)

    API->>DB: Salva minuta de prontuário e guia do tutor
    API-->>App: Renderiza Prontuário SOAP formatado na tela do Veterinário

    V->>App: Revisa minuta, ajusta detalhes e clica em "Assinar Prontuário"
    App->>API: POST /api/consultations/{id}/finalize
    API->>DB: Prontuário assinado permanentemente
    API-->>T: Dispara Guia de Cuidados no WhatsApp/App do Tutor
```

---

## 4. Estratégia de Resiliência e Operação Offline

Clínicas veterinárias frequentemente enfrentam oscilações de sinal de internet em salas de exame com blindagem ou subsolos. Para garantir operação ininterrupta:

1. **Local-First Audio Buffer (IndexedDB no Navegador / SQLite no App Mobile)**:
   - Os chunks de áudio são gravados e persistidos localmente no dispositivo durante a consulta em formato WebM/Opus comprimido.
   - Em caso de perda repentina de conexão, o áudio permanece íntegro na memória do cliente e é reenviado automaticamente assim que o link for restaurado.
2. **Fallback Híbrido de Modelos**:
   - *Modo Nuvem (Online)*: ASR via Whisper-Large / Gemini Multimodal com processamento assíncrono em GPU na nuvem.
   - *Modo Local / Borda (Edge Fallback)*: Para clínicas sem conexão externa estável, suporte à execução local do Whisper-Tiny / Small via ONNX Runtime na máquina da clínica.

---

## 5. Segurança da Informação, LGPD e Padrões Médicos

- **Criptografia Ponta a Ponta**: Áudios são trafegados via TLS 1.3 e armazenados em repouso com algoritmo AES-256.
- **Anonimização de PII (Personally Identifiable Information)**: O módulo de pré-processamento realiza higienização de nomes completos, CPFs, placas de carro ou números de cartão mencionados na consulta antes do envio ao motor generativo.
- **Padrão SOAP Padronizado**: Estruturação estrita de acordo com as normas da *American Animal Hospital Association (AAHA)* e do *Conselho Federal de Medicina Veterinária (CFMV)*.
