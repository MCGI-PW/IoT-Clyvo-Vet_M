# Roteiro do Vídeo Pitch (5 Minutos): ClyvoScribe AI para CLYVO VET

> **Instruções Gerais de Gravação**:
> - **Duração Total**: Exatamente entre 04:45 e 05:15 (alvo ideal: 5 minutos cravados).
> - **Formato de Publicação**: YouTube (configurar visibilidade como **Não Listado / Unlisted**).
> - **Configuração de Cena Recomendada**: Alternar entre câmera do apresentador (webcam no canto ou tela cheia na introdução/conclusão) e gravação de tela exibindo os slides e a demonstração prática da aplicação web.

---

## Estrutura Cronometrada do Pitch

```
[00:00 - 00:50] BLOCO 1: O Problema Real e a Oportunidade na Consulta Veterinária (50s)
[00:50 - 02:00] BLOCO 2: A Solução e Demonstração Prática Funcional (70s)
[00:02 - 03:15] BLOCO 3: Arquitetura Técnica e o Papel da IA (75s)
[03:15 - 04:15] BLOCO 4: Fluxo de Dados, Segurança e Apoio à Decisão (60s)
[04:15 - 05:00] BLOCO 5: Impacto de Negócio (Tutor, Clínica, Pet) e Conclusão (45s)
```

---

## Roteiro Teleprompter & Direção de Cena

### BLOCO 1: O Problema Real na Jornada Clínica (00:00 – 00:50)
**[Câmera em tela cheia no apresentador, tom seguro e empático]**

> *"Olá! Você já reparou como funciona uma consulta veterinária típica hoje?*  
> *O tutor chega aflito com o seu pet doente. O médico-veterinário acolhe o paciente, mas logo é obrigado a virar de costas para o animal e passar até 40% do tempo da consulta digitando anotações em um prontuário eletrônico lento e engessado.*  
> *Essa distração não é apenas desconfortável: ela aumenta o estresse do animal na mesa de exame e gera fadiga mental no profissional.*  
> *Para piorar, do outro lado, o tutor sai da clínica sobrecarregado, esquecendo mais da metade das orientações verbais sobre horários de remédios e sinais de perigo.*  
> *Na CLYVO VET, nós decidimos mudar essa realidade radicalmente com Inteligência Artificial: apresentamos o **ClyvoScribe AI**, a inteligência clínica ambiental que devolve a atenção do veterinário para o que realmente importa — a vida do paciente."*

---

### BLOCO 2: A Solução & Demonstração Funcional Prática (00:50 – 02:00)
**[Corta para gravação de tela: mostrando a interface web do ClyvoScribe AI em execução]**

> *"Vejam como funciona na prática.*  
> *Aqui no painel da CLYVO VET, o veterinário inicia o atendimento do paciente — neste exemplo, o cão Thor, um Buldogue Francês de 3 anos.*  
> *Com o consentimento do tutor, o veterinário simplesmente clica em **'Iniciar Escuta Inteligente'**.*  
> *Durante toda a conversa e o exame físico, ninguém digita uma única linha. O sistema capta o diálogo ambiental em tempo real.*  
> *Ao clicar em **'Encerrar e Processar'**, a nossa IA entra em ação instantaneamente:*  
> *1. O motor de reconhecimento de fala transcreve o diálogo médico com alta fidelidade terminológica.*  
> *2. Em segundos, o modelo de linguagem estruturado organiza toda a consulta no padrão ouro internacional **SOAP**: Subjetivo com as queixas do tutor, Objetivo com os dados do exame físico e temperatura, Avaliação com o diagnóstico de otite e dermatite, e Plano com a prescrição precisa de medicamentos e exames.*  
> *3. E notem o mais impressionante: o sistema já disparou automaticamente alertas de segurança farmacológica com base na raça e peso do paciente!"*

---

### BLOCO 3: Arquitetura Técnica e o Papel da IA (02:00 – 03:15)
**[Tela dividida: Slide com o Diagrama de Arquitetura Mermaid e destaques visuais]**

> *"Mas como essa mágica acontece debaixo do capô?*  
> *O ClyvoScribe AI não é apenas um transcritor comum de áudio; ele opera com uma **arquitetura híbrida em três camadas** integrada ao backend FastAPI da CLYVO VET:*  
> *Na **Primeira Camada**, utilizamos um modelo avançado de ASR (Whisper / Gemini Multimodal) especializado no léxico médico-veterinário em português brasileiro, capaz de isolar latidos e ruídos da clínica e realizar diarização de locutores.*  
> *Na **Segunda Camada**, os textos diarizados são enriquecidos com o prontuário pregresso do pet e processados por um LLM com **Structured Outputs** via Pydantic. Isso garante zero alucinações sintáticas e extrai entidades clínicas perfeitamente tipadas.*  
> *E na **Terceira Camada**, implementamos um **Motor Determinístico de Regras Clínicas**. Nós não deixamos dosagens e contraindicações a cargo de probabilidades estatísticas. Essa camada cruza os fármacos prescritos com diretrizes da WSAVA e do CFMV, validando pesos, toxicidades raciais como a mutação MDR1 e interações medicamentosas.*  
> *Essa união entre IA Generativa e IA Simbólica Determinística entrega a máxima inovação com 100% de segurança médica."*

---

### BLOCO 4: Fluxo de Dados, Segurança e Personalização (03:15 – 04:15)
**[Slide mostrando o Fluxo de Dados e a tela 'Visão do Tutor' no protótipo]**

> *"O fluxo de dados foi desenhado respeitando rigorosamente a LGPD e o sigilo veterinário.*  
> *Os dados brutos de áudio trafegam criptografados e passam por anonimização prévia de informações pessoais sensíveis.*  
> *A personalização é o coração do sistema:*  
> *A partir do mesmo atendimento, a IA gera simultaneamente duas saídas de alto valor:*  
> *Primeiro, a **Visão Clínica Técnica**, validada e assinada pelo veterinário com seu número de CRMV.*  
> *Segundo, a **Visão do Tutor**: um guia humanizado gerado pela IA em linguagem acolhedora, enviado diretamente para o WhatsApp ou app do tutor. Ele contém uma tabela clara de medicação, horários organizados, alarmes configurados e alertas do que observar em casa.*  
> *Isso acaba com a caligrafia ilegível e multiplica a adesão ao tratamento!"*

---

### BLOCO 5: Benefícios de Negócio e Conclusão (04:15 – 05:00)
**[Câmera volta para o apresentador com slide de métricas ao fundo]**

> *"Os resultados desse ecossistema transformam o modelo de negócio da clínica:*  
> *Para a **Clínica**, reduzimos em até 70% o tempo administrativo por paciente, permitindo atender mais pets sem sobrecarga, além de sugerir de forma proativa faturamento de exames complementares e retornos que antes eram esquecidos.*  
> *Para o **Tutor**, entregamos clareza, segurança e tranquilidade no cuidado diário do seu melhor amigo.*  
> *E para o **Pet**, garantimos um veterinário com olhos, mãos e mente 100% focados nele durante todo o exame.*  
> *O ClyvoScribe AI une a fronteira da Inteligência Artificial à compaixão veterinária. O código-fonte, a documentação de arquitetura e o protótipo executável estão disponíveis no nosso repositório no GitHub.*  
> *Muito obrigado!"*

---

## Dicas para o Vídeo Tirar Nota Máxima (20/20 Pontos)
1. **Áudio Nítido**: Use um fone com microfone bom ou microfone de lapela.
2. **Iluminação**: Garanta que seu rosto esteja bem iluminado se usar câmera.
3. **Fluidez**: Ensaiar o texto 2 a 3 vezes antes de gravar garante que o tempo fique exatamente na faixa de 4:50 a 5:05.
4. **Demonstração Funcional**: Mostre a tela do dashboard web do projeto (`http://localhost:8000`) rodando a transcrição e gerando o SOAP ao vivo durante o Bloco 2!
