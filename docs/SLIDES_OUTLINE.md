# Guia de Slides para o Vídeo Pitch: ClyvoScribe AI (CLYVO VET)

Use esta estrutura de 6 a 7 slides caso queira projetar uma apresentação no Canva, PowerPoint ou Google Slides enquanto grava seu pitch:

---

### Slide 1: Capa
- **Título**: CLYVO VET — ClyvoScribe AI
- **Subtítulo**: Inteligência Clínica Ambiental e Apoio à Decisão Veterinária
- **Elementos Visuais**: Logo da CLYVO VET, ícone de ondas sonoras unidas a uma pata de pet, identificação dos integrantes do grupo e data.

---

### Slide 2: O Problema na Consulta Tradicional
- **Título**: A Crise Invisível na Sala de Consulta
- **Tópicos**:
  - **40% do tempo** da consulta é perdido com digitação manual de prontuário.
  - **Sobrecarga cognitiva e burnout** de médicos-veterinários.
  - **50% das orientações verbais** são esquecidas pelos tutores após sair da clínica.
  - **Subnotificação e evasão**: exames e retornos citados verbalmente, mas não faturados ou agendados.
- **Elemento Visual**: Comparativo visual (Veterinário de costas digitando vs. Pet estressado na mesa).

---

### Slide 3: A Solução ClyvoScribe AI
- **Título**: Da Escuta Ativa à Decisão Clínica em Segundos
- **Tópicos**:
  - Escuta ambiental consentida durante o atendimento.
  - Transcrição especializada com termos médicos veterinários (ASR).
  - Estruturação automática no padrão internacional **SOAP** (*Subjective, Objective, Assessment, Plan*).
  - Alertas automáticos de dosagens e contraindicações farmacológicas.
- **Elemento Visual**: [Momento para colocar a gravação de tela com a demonstração funcional ao vivo].

---

### Slide 4: Arquitetura Técnica em 3 Camadas
- **Título**: Arquitetura Híbrida: Inovação e Rigor Clínico
- **Tópicos**:
  - **Camada 1 (ASR)**: Whisper / Multimodal com cancelamento de ruído e diarização.
  - **Camada 2 (Clinical LLM)**: Extração de entidades e redação SOAP com Pydantic Structured Outputs.
  - **Camada 3 (Safety Guardrail)**: Motor determinístico de regras baseado em CFMV e genética de raças (MDR1, braquicefálicos).
- **Elemento Visual**: Diagrama de blocos da arquitetura (conforme documentado em `docs/ARCHITECTURE.md`).

---

### Slide 5: Fluxo de Dados e Personalização Dupla
- **Título**: Da Voz ao Cuidado Contínuo (Segurança & LGPD)
- **Tópicos**:
  - **Visão Veterinária**: Prontuário técnico auditado pronto para assinatura digital.
  - **Visão do Tutor**: Resumo humanizado no WhatsApp com cronograma de medicamentos e alarmes.
  - **Segurança LGPD**: Criptografia de ponta a ponta e anonimização de dados sensíveis de voz.
- **Elemento Visual**: Exemplo visual do WhatsApp do tutor lado a lado com o prontuário clínico.

---

### Slide 6: Proposta de Valor e Impacto de Negócio
- **Título**: Benefícios para Todo o Ecossistema
- **Tópicos**:
  - **Para a Clínica**: +35% de capacidade de consultas, retenção de clientes e zero esquecimento de exames.
  - **Para o Tutor**: Maior adesão ao tratamento, sem dúvidas ou erros de medicação.
  - **Para o Pet**: Consulta acolhedora, exame físico minucioso e atenção 100% focada nele.
- **Elemento Visual**: Gráfico de pizza ou cards com métricas de impacto (+35% eficiência, -70% tempo de digitação).

---

### Slide 7: Conclusão & Repositório
- **Título**: O Futuro da Medicina Veterinária Começa Aqui
- **Tópicos**:
  - Código-fonte, testes e protótipo disponíveis no GitHub.
  - Demonstração funcional executável localmente com 1 comando.
  - Agradecimentos e contato.
- **Elemento Visual**: QR Code para o repositório no GitHub.
