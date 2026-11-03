# Slides de apoio ao pitch: AuroraScribe AI

Seis slides para projetar enquanto grava o pitch ([roteiro](PITCH_SCRIPT_5MIN.md)). As demonstrações são gravações de tela, não slides.

---

### Slide 1: Capa
- **Título:** Aurora Pet · AuroraScribe AI
- **Subtítulo:** Transcrição inteligente da consulta veterinária
- **Rodapé:** Maicon Douglas (RM561279), Gabriel F. (RM561551), Charlles (RM566482), Iago D. (RM565708)

### Slide 2: O problema
- O veterinário divide a atenção entre o animal e o teclado.
- O prontuário sai incompleto.
- O tutor esquece dose, horário e sinais de alerta.
- Contraindicações por raça e doença dependem da memória.

### Slide 3: A solução
- Fala da consulta → **minuta SOAP** para o veterinário revisar.
- **Alertas de segurança** pelo perfil do pet (MDR1, felino renal, braquicefálico, vacinas).
- **Resumo simples** para o tutor e **sugestões** de exames e retorno para a clínica.
- A IA sugere, o veterinário decide.

### Slide 4: Arquitetura em três camadas
- **1. Fala → texto:** Web Speech API ao vivo · Whisper para áudio gravado.
- **2. Texto → SOAP:** Claude com saída estruturada · extrator local quando não há Claude.
- **3. Segurança:** regras clínicas determinísticas.
- **Visual:** diagrama do README (painel → API Java → AuroraScribe → Claude/regras → Oracle).

### Slide 5: Resultados
- Tabela da seção "Resultados parciais" do README (Thor, Mel, Bob e consulta livre).
- 14 testes automatizados passando.
- Resiliência: Claude → extrator local; AuroraScribe → assistente local do Java.

### Slide 6: Valor e próximos passos
- **Veterinário:** menos digitação. **Pet:** mais segurança. **Tutor:** orientações claras. **Clínica:** exames e retornos que não se perdem.
- **Próximos passos:** envio do resumo por WhatsApp, perfil clínico completo na integração, AuroraScribe online no Azure.
- QR Code para o repositório: `github.com/MCGI-PW/IoT-Clyvo-Vet_M`
