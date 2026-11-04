# Roteiro do Vídeo Pitch (5 minutos): AuroraScribe AI

> **Formato:** YouTube, visibilidade **Não listado**. Duração entre 4:45 e 5:15.
> **Cena:** câmera do apresentador na abertura e no fechamento; no meio, gravação de tela.
> **Antes de gravar:** suba os dois serviços como no README ("Integrado com a Aurora Pet"), use o **Chrome** e deixe o microfone permitido em `localhost`. Os dados de demonstração da Aurora Pet já trazem um atendimento agendado do Thor (Golden Retriever) com o Dr. Carlos.

| Tempo | Bloco | Tela |
|---|---|---|
| 0:00–0:40 | 1. Problema | Câmera |
| 0:40–1:40 | 2. Demonstração: AuroraScribe | `http://localhost:8000` |
| 1:40–3:00 | 3. Demonstração: integrado à Aurora Pet | `http://localhost:8081` (painel do veterinário) |
| 3:00–4:10 | 4. Como a IA funciona | Diagrama do README |
| 4:10–5:00 | 5. Resultados, valor e fechamento | Tabela de resultados do README + câmera |

---

### Bloco 1: o problema (0:00–0:40)
**[Câmera]**

> *"Numa consulta veterinária, o profissional divide a atenção entre o animal e o teclado. O prontuário sai às pressas e incompleto. O tutor vai embora sem lembrar a dose nem o horário do remédio. E um risco sério, como um medicamento perigoso para a raça do cão, depende só da memória de quem está atendendo.*
> *Para a Aurora Pet, criamos o **AuroraScribe AI**: a IA ouve a consulta, escreve o prontuário, confere a segurança da prescrição e explica tudo para o tutor. E o veterinário continua no controle."*

### Bloco 2: o AuroraScribe em ação (0:40–1:40)
**[Tela: interface do AuroraScribe]**

> *"Este é o AuroraScribe. Vou escolher o Bob, um Border Collie, e carregar a consulta dele."*

- Selecionar **Bob** e carregar o caso de exemplo. Processar.
- Mostrar a aba **Prontuário SOAP**: queixa, exame, diagnóstico e prescrição com dose, intervalo e duração. Apontar a etiqueta da **fonte da IA**.
- Mostrar a aba **Alertas Clínicos**:

> *"Na conversa, o tutor citou ivermectina e loperamida. Border Collie tem alta chance de mutação no gene MDR1, e esses remédios podem causar neurotoxicidade. O sistema marcou em vermelho, sem ninguém pedir."*

- Mostrar rapidamente a **Visão do Tutor** (horários e sinais de alerta) e a **Gestão da Clínica** (raio-x e retorno sugeridos).

### Bloco 3: integrado à Aurora Pet (1:40–3:00)
**[Tela: painel do veterinário na Aurora Pet]**

> *"Agora, dentro da plataforma. Estou logado como o Dr. Carlos, no atendimento do Thor."*

- Clicar em **🎙️ Iniciar transcrição** e falar (devagar, frase a frase):

```text
O Thor está coçando muito a orelha direita há três dias.
A orelha está vermelha e com secreção. Parece ser uma otite externa.
Vou prescrever solução otológica, 3 gotas duas vezes ao dia por 7 dias.
Mantenha a orelha seca. Se ele tiver febre ou parar de comer, volte antes.
Retorno em 10 dias.
```

> *"O texto aparece enquanto eu falo. Quando eu peço o resumo, a API Java manda a transcrição, só com o nome e a raça do pet, para o AuroraScribe."*

- Clicar em **⏹ Parar transcrição** e depois em **✨ Gerar resumo com IA**. Mostrar diagnóstico, prescrição, orientações, resumo para o tutor e sinais de alerta preenchidos.

> *"A sugestão foi gravada no Oracle, na tabela de transcrições. Mas ela ainda não é prontuário: eu reviso, corrijo se precisar, e só quando concluo o atendimento ela vira o registro oficial, que o tutor vê no painel dele."*

- Concluir o atendimento.

### Bloco 4: como a IA funciona (3:00–4:10)
**[Tela: diagrama de arquitetura do README]**

> *"São três camadas.*
> *Na primeira, o reconhecimento de fala do navegador transcreve a consulta em português, ao vivo. Áudios gravados podem passar pelo Whisper.*
> *Na segunda, o Claude, da Anthropic, organiza a conversa no padrão SOAP, com saída estruturada: a resposta sempre chega no mesmo formato, e o prompt proíbe inventar remédio, dose ou prazo. Sem internet ou sem chave, um extrator local por regras assume e usa só as frases que foram ditas.*
> *Na terceira, regras clínicas determinísticas cruzam a prescrição com a espécie, a raça, as doenças crônicas e as vacinas do pet. Contraindicação grave não fica a cargo de probabilidade.*
> *E se o AuroraScribe cair, a API Java usa o assistente local dela: a consulta nunca trava. Cada resumo guarda qual IA o gerou."*

### Bloco 5: resultados e fechamento (4:10–5:00)
**[Tela: seção "Resultados parciais" do README, depois câmera]**

> *"Testamos com três casos reais de clínica e com consultas livres. A IA detectou a contraindicação de ivermectina no Border Collie, o anti-inflamatório na gata com doença renal e a vacina atrasada do Thor. São 14 testes automatizados, inclusive garantindo que nada é inventado numa consulta livre.*
> *Para o veterinário, menos digitação e mais atenção ao paciente. Para o pet, mais segurança. Para o tutor, orientações claras. E para a clínica, exames e retornos que não se perdem.*
> *O código e a documentação estão no nosso GitHub. Obrigado!"*

---

## Dicas
1. **Ensaie uma vez cronometrando.** Se passar de 5:15, encurte o bloco 2.
2. **Áudio:** use fone com microfone e fale pausado no bloco 3, para a legenda acompanhar.
3. **Plano B do bloco 3:** se o microfone falhar, cole o texto do roteiro na caixa de transcrição. O resultado é o mesmo.
4. **Mostre a fonte da IA** nos dois blocos de demonstração: é a prova da integração.
