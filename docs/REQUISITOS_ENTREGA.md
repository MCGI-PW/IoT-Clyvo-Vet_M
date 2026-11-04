# Requisitos da entrega: Sprint 4 (Disruptive Architectures: IoT, IoB & Generative IA)

Cada requisito do Challenge, com a evidência de onde ele foi atendido. Os tempos levam direto ao trecho do vídeo pitch.

- **Vídeo pitch:** https://youtu.be/3mCGLHQrmjg (4 min 32 s, público no YouTube, abre sem login)
- **Repositório:** https://github.com/MCGI-PW/IoT-Clyvo-Vet_M
- **Aplicação integrada (Aurora Pet, API Java):** https://github.com/MCGI-PW/API-Clyvo-M_Vet

## Entregáveis obrigatórios

| Requisito | Status | Evidência |
|---|:---:|---|
| Arquivo `.zip` | ✅ | `AURORA_PET_ENTREGA_IA.zip`, gerado por [`scripts/package_submission.sh`](../scripts/package_submission.sh): código versionado + `ENTREGA.txt` com os links e os integrantes |
| Link do vídeo no YouTube | ✅ | https://youtu.be/3mCGLHQrmjg, no `ENTREGA.txt` e no topo do [README](../README.md) |
| Vídeo com a ideia central do projeto | ✅ | Problema e solução em [0:00](https://youtu.be/3mCGLHQrmjg?t=0) |
| Vídeo com demonstração funcional dos principais recursos | ✅ | Demonstração real: AuroraScribe em [0:47](https://youtu.be/3mCGLHQrmjg?t=47), integração com a Aurora Pet em [2:03](https://youtu.be/3mCGLHQrmjg?t=123) |
| Link do repositório no GitHub | ✅ | https://github.com/MCGI-PW/IoT-Clyvo-Vet_M, no `ENTREGA.txt` |
| Código-fonte e estrutura do projeto | ✅ | [`app/`](../app), [`tests/`](../tests), [`samples/`](../samples); mapa em [Estrutura do repositório](../README.md#-estrutura-do-repositório) |
| README com instruções de uso | ✅ | [Como executar](../README.md#-como-executar) e [Como usar a interface de demonstração](../README.md#%EF%B8%8F-como-usar-a-interface-de-demonstração) |
| README com tecnologias utilizadas | ✅ | [Tecnologias](../README.md#%EF%B8%8F-tecnologias) |
| README com resultados parciais | ✅ | [Resultados parciais](../README.md#-resultados-parciais): Thor, Mel, Bob e consulta livre |

## Objetivos principais

| Requisito | Status | Evidência |
|---|:---:|---|
| Implementar a solução de IA definida na entrega anterior | ✅ | Pipeline em [`app/services/pipeline.py`](../app/services/pipeline.py), seguindo a [especificação da IA](AI_SPECIFICATION.md) |
| Integrar a IA à aplicação da Aurora Pet | ✅ | A API Java chama `POST /api/transcriptions/summarize` ([`run_server.py`](../run_server.py), [`app/main.py`](../app/main.py)); no vídeo em [2:03](https://youtu.be/3mCGLHQrmjg?t=123) |
| Demonstrar o funcionamento com testes, documentação técnica e vídeo pitch | ✅ | 14 testes em [`tests/`](../tests), documentação em [`docs/`](.), vídeo de 4 min 32 s |
| Vídeo de aproximadamente 5 minutos destacando o funcionamento da IA | ✅ | 4 min 32 s; como a IA funciona em [2:55](https://youtu.be/3mCGLHQrmjg?t=175) |
| Benefícios para o tutor e para a clínica | ✅ | Guia do tutor e sugestões para a clínica em [1:39](https://youtu.be/3mCGLHQrmjg?t=99); [Solução e valor](../README.md#-solução-e-valor) |
| Integração com os demais componentes do sistema | ✅ | Aurora Pet → AuroraScribe → Aurora Pet em [2:18](https://youtu.be/3mCGLHQrmjg?t=138); containers no Azure em [3:37](https://youtu.be/3mCGLHQrmjg?t=217) |

## Objetivos específicos

| Requisito | Status | Evidência |
|---|:---:|---|
| Desenvolver a funcionalidade de IA especificada | ✅ | Claude com saída estruturada ([`claude_extractor.py`](../app/services/claude_extractor.py)), plano B local ([`local_extractor.py`](../app/services/local_extractor.py)), regras clínicas ([`decision_support.py`](../app/services/decision_support.py)) e guia do tutor ([`tutor_care_generator.py`](../app/services/tutor_care_generator.py)) |
| Uso da IA integrado e transparente ao usuário | ✅ | Botão "Gerar resumo com IA" no painel do veterinário e selo da fonte (`IA: AURORASCRIBE`) em [2:36](https://youtu.be/3mCGLHQrmjg?t=156) |
| Comunicação entre interface, banco de dados, APIs e serviços inteligentes | ✅ | [Arquitetura e integração](../README.md#%EF%B8%8F-arquitetura-e-integração-com-a-aurora-pet); a API Java grava a sugestão na tabela `TRANSCRICAO_CONSULTA` ([Dicionário de dados, seção 3](DATA_DICTIONARY.md)); log real do servidor com `POST ... 200` em [2:40](https://youtu.be/3mCGLHQrmjg?t=160) |
| Testar e validar em cenários reais de uso | ✅ | 3 casos clínicos + 1 consulta livre ([`samples/`](../samples)); 14 testes passando em [4:07](https://youtu.be/3mCGLHQrmjg?t=247) |
| Avaliar os resultados e mostrar a personalização para o tutor e o acompanhamento da saúde do pet | ✅ | [Resultados parciais](../README.md#-resultados-parciais); alertas por raça, doença crônica e vacina ([especificação, seção 3](AI_SPECIFICATION.md)) |

## Tarefas

| Requisito | Status | Evidência |
|---|:---:|---|
| Implementar a IA (IA generativa, LLM, regras ou outra abordagem) | ✅ | Arquitetura híbrida em três camadas: [Abordagem de IA](../README.md#-abordagem-de-ia) |
| Preparar e organizar os dados, com testes e validação | ✅ | [`samples/pet_profiles.json`](../samples/pet_profiles.json), [`samples/audio_transcripts.json`](../samples/audio_transcripts.json), [Dados utilizados](../README.md#%EF%B8%8F-dados-utilizados), [Dicionário de dados](DATA_DICTIONARY.md) |
| Mecanismos de integração entre aplicação, banco, APIs e IA | ✅ | Contrato da API em [Dicionário de dados, seção 3](DATA_DICTIONARY.md); [Arquitetura](ARCHITECTURE.md) |
| Funcionalidade acessível ao usuário final e com valor para a jornada do tutor | ✅ | Painel do veterinário na Aurora Pet; prontuário que o tutor vê no painel dele, em [2:51](https://youtu.be/3mCGLHQrmjg?t=171) |
| Evidências do funcionamento (telas, fluxos, relatórios ou demonstrações) | ✅ | [`docs/evidencias/`](evidencias) e o vídeo pitch |

## Critérios de avaliação

| Critério | Pontos | Onde avaliar |
|---|:---:|---|
| Aplicação técnica de conceitos de IA | até 60 | LLM com saída estruturada, plano B local, regras determinísticas e fonte da IA rastreável: [Abordagem de IA](../README.md#-abordagem-de-ia), [especificação](AI_SPECIFICATION.md), [arquitetura](ARCHITECTURE.md) |
| Clareza e didática da apresentação em vídeo | até 20 | https://youtu.be/3mCGLHQrmjg (narração, capítulos e demonstração real) |
| Organização do repositório e documentação técnica | até 20 | [README](../README.md), [`docs/`](.), [Estrutura do repositório](../README.md#-estrutura-do-repositório) |

## Observação

O Challenge pede o vídeo em modo **não listado**. O grupo decidiu publicá-lo como **público**: o link abre sem login, como na visibilidade não listada.
