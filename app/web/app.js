// CLYVO VET — ClyvoScribe AI Client Logic
let currentPetId = "PET-8921";
let currentSelectedCase = "CASE-THOR-OTITE";
let isRecording = false;
let recognition = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initPetSelector();
  initSampleButtons();
  initControls();
  // Carrega pet inicial
  loadPetData(currentPetId);
});

// Navegação por Abas
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(target)?.classList.add("active");
    });
  });
}

// Inicialização do Seletor de Pets
function initPetSelector() {
  const petSelect = document.getElementById("petSelect");
  petSelect.addEventListener("change", (e) => {
    currentPetId = e.target.value;
    loadPetData(currentPetId);
    // Vincula o caso de exemplo correspondente
    if (currentPetId === "PET-8921") currentSelectedCase = "CASE-THOR-OTITE";
    else if (currentPetId === "PET-4102") currentSelectedCase = "CASE-MEL-RENAL";
    else if (currentPetId === "PET-6734") currentSelectedCase = "CASE-BOB-COLLIE";
  });
}

// Botões de Casos Pré-gravados
function initSampleButtons() {
  const sampleBtns = document.querySelectorAll(".sample-btn");
  sampleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      currentSelectedCase = btn.dataset.case;
      // Caso de exemplo escolhido: a transcrição vem da amostra gravada, não do campo de texto
      document.getElementById("liveTranscript").value = "";
      sampleBtns.forEach(b => b.classList.remove("btn-primary"));
      btn.classList.add("btn-primary");
      
      if (currentSelectedCase === "CASE-THOR-OTITE") {
        document.getElementById("petSelect").value = "PET-8921";
        currentPetId = "PET-8921";
      } else if (currentSelectedCase === "CASE-MEL-RENAL") {
        document.getElementById("petSelect").value = "PET-4102";
        currentPetId = "PET-4102";
      } else if (currentSelectedCase === "CASE-BOB-COLLIE") {
        document.getElementById("petSelect").value = "PET-6734";
        currentPetId = "PET-6734";
      }
      loadPetData(currentPetId);
      animateVisualizer(true, "Áudio da consulta carregado e pronto para análise");
    });
  });
}

// Controles de Gravação e Processamento
function initControls() {
  const btnProcess = document.getElementById("btnProcessAI");
  btnProcess.addEventListener("click", () => {
    processConsultation(currentPetId, currentSelectedCase);
  });

  const btnMic = document.getElementById("btnMicToggle");
  btnMic.addEventListener("click", () => {
    toggleMicrophone();
  });

  const btnSign = document.getElementById("btnSignSoap");
  btnSign.addEventListener("click", () => {
    alert("✅ Prontuário assinado digitalmente com sucesso pelo Dr(a). Veterinário(a) (CRMV-SP 45.892)!\n\nO documento foi registrado no prontuário eletrônico permanente da CLYVO VET e o Guia do Tutor foi disparado via WhatsApp.");
  });
}

// Carregar Dados do Pet via API
async function loadPetData(petId) {
  try {
    const res = await fetch(`/api/pets/${petId}`);
    if (!res.ok) throw new Error("Erro ao buscar pet");
    const pet = await res.json();

    document.getElementById("petName").innerText = pet.nome;
    document.getElementById("petBreed").innerText = `${pet.raca} • ${pet.especie.toUpperCase()} • ${pet.sexo.toUpperCase()}`;
    document.getElementById("petWeight").innerText = `${pet.peso_atual_kg} kg`;
    document.getElementById("petAge").innerText = `${pet.idade_anos} anos`;
    document.getElementById("petTutor").innerText = pet.tutor_nome;
    document.getElementById("petPhone").innerText = pet.tutor_telefone;
    document.getElementById("petAvatar").innerText = pet.especie === "felina" ? "🐱" : "🐶";

    const comorbText = pet.comorbidades_cronicas.length > 0 ? pet.comorbidades_cronicas.join(", ") : "Nenhuma comorbidade prévia";
    document.getElementById("petComorbidities").innerText = comorbText;

    const vacAtrasada = pet.historico_vacinal.find(v => v.status === "atrasada");
    const vacBadge = document.getElementById("petVaccineStatus");
    if (vacAtrasada) {
      vacBadge.className = "pet-badge badge-alert";
      vacBadge.innerText = `Vacina ${vacAtrasada.vacina} Atrasada`;
    } else {
      vacBadge.className = "pet-badge badge-ok";
      vacBadge.innerText = "Vacinas em Dia";
    }
  } catch (err) {
    console.error("Falha ao carregar dados do pet:", err);
  }
}

// Transcrição ao vivo com o reconhecimento de voz do navegador (Web Speech API)
function toggleMicrophone() {
  if (isRecording) {
    isRecording = false;
    if (recognition) recognition.stop();
    setMicButton(false);
    document.getElementById("liveInterim").innerText = "";
    animateVisualizer(false, "Escuta finalizada. Revise o texto e clique em Processar Consulta.");
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    animateVisualizer(false, "Este navegador não tem reconhecimento de voz (use Chrome ou Edge). Cole a transcrição no campo abaixo.");
    return;
  }

  const transcriptBox = document.getElementById("liveTranscript");
  const interimBox = document.getElementById("liveInterim");
  // Uma consulta nova pelo microfone não usa o caso de exemplo selecionado
  currentSelectedCase = null;
  document.querySelectorAll(".sample-btn").forEach(b => b.classList.remove("btn-primary"));

  recognition = new SpeechRecognition();
  recognition.lang = "pt-BR";
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event) => {
    let parcial = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const trecho = event.results[i][0].transcript.trim();
      if (event.results[i].isFinal) {
        const atual = transcriptBox.value.trim();
        transcriptBox.value = (atual ? atual + " " : "") + capitalizar(trecho) + ".";
        transcriptBox.scrollTop = transcriptBox.scrollHeight;
      } else {
        parcial += trecho + " ";
      }
    }
    // Legenda em tempo real, como a tradução simultânea dos fones de ouvido
    interimBox.innerText = parcial;
  };

  recognition.onerror = (event) => {
    if (event.error === "not-allowed" || event.error === "service-not-allowed") {
      isRecording = false;
      setMicButton(false);
      animateVisualizer(false, "Permissão do microfone negada. Libere o microfone ou cole a transcrição.");
    }
  };

  // O navegador encerra a escuta após pausas longas; reinicia enquanto o veterinário não finalizar
  recognition.onend = () => {
    if (isRecording) recognition.start();
  };

  recognition.start();
  isRecording = true;
  setMicButton(true);
  animateVisualizer(true, "🔴 Escutando a consulta: o texto aparece em tempo real abaixo.");
}

function setMicButton(gravando) {
  const btnMic = document.getElementById("btnMicToggle");
  btnMic.classList.toggle("btn-danger", !gravando);
  btnMic.classList.toggle("btn-success", gravando);
  btnMic.innerHTML = gravando
    ? "<span>⏹️</span> Finalizar Escuta"
    : "<span>🔴</span> Iniciar Escuta (Microfone)";
}

function capitalizar(texto) {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function animateVisualizer(active, text) {
  const box = document.getElementById("visualizerBox");
  const txt = document.getElementById("visualizerText");
  if (active) {
    box.classList.add("active");
  } else {
    box.classList.remove("active");
  }
  if (text) txt.innerText = text;
}

// Processar Consulta no Backend
async function processConsultation(petId, caseId) {
  if (!caseId && !document.getElementById("liveTranscript").value.trim()) {
    alert("Fale a consulta pelo microfone, cole uma transcrição ou escolha um caso gravado de exemplo.");
    return;
  }
  const loading = document.getElementById("loadingIndicator");
  const content = document.getElementById("tabContentArea");

  loading.style.display = "block";
  content.style.opacity = "0.3";

  try {
    const res = await fetch("/api/consultations/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Texto do campo (falado ao vivo ou colado) tem prioridade sobre o caso de exemplo
      body: JSON.stringify({
        pet_id: petId,
        sample_case_id: caseId,
        custom_transcript: document.getElementById("liveTranscript").value.trim() || null
      })
    });

    if (!res.ok) throw new Error("Erro no processamento da consulta");
    const result = await res.json();
    renderConsultationResult(result);
  } catch (err) {
    console.error("Falha no pipeline de IA:", err);
    alert("Erro ao processar consulta: " + err.message);
  } finally {
    loading.style.display = "none";
    content.style.opacity = "1.0";
  }
}

// Renderizar Resultados
function renderConsultationResult(data) {
  // 1. SOAP
  const fonte = data.soap.fonte_ia || "";
  const fonteLabel = fonte.startsWith("CLAUDE") ? `IA: ${fonte.replace("CLAUDE:", "Claude ")}`
    : fonte === "LOCAL:protocolo-demo" ? "Protocolo de demonstração" : "Extração local por regras";
  document.getElementById("consultationIdBadge").innerHTML =
    `${data.consultation_id} • Processado em ${data.tempo_processamento_segundos}s <span class="fonte-badge">${fonteLabel}</span>`;
  
  // Subjetivo
  document.getElementById("soapQueixa").innerText = data.soap.subjective.queixa_principal || "-";
  document.getElementById("soapHMA").innerText = data.soap.subjective.historico_molestia_atual || "-";
  document.getElementById("soapAlimentacao").innerText = data.soap.subjective.alimentacao_e_apetite || "-";

  // Objetivo
  const vit = data.soap.objective.parametros_vitais;
  document.getElementById("soapVitais").innerHTML = `
    <span class="vital-badge">🌡️ Temp: ${vit.temperatura_retal_c ?? "-"} °C</span>
    <span class="vital-badge">❤️ FC: ${vit.frequencia_cardiaca_bpm ?? "-"} bpm</span>
    <span class="vital-badge">🫁 FR: ${vit.frequencia_respiratoria_mpm ?? "-"} mpm</span>
    <span class="vital-badge">💧 Desidratação: ${vit.grau_desidratacao_pct ?? "-"}%</span>
  `;
  document.getElementById("soapGeral").innerText = data.soap.objective.exame_fisico_geral || "-";
  document.getElementById("soapEspecifico").innerText = data.soap.objective.exame_fisico_especifico || "-";

  // Avaliação
  const diagList = document.getElementById("soapDiagnosticos");
  diagList.innerHTML = data.soap.assessment.hipoteses_diagnosticas
    .map(d => `<li style="font-weight: 600; color: #0f172a; margin-bottom: 3px;">${d}</li>`)
    .join("");

  const gravBadge = document.getElementById("soapGravidade");
  const grav = data.soap.assessment.nivel_gravidade;
  gravBadge.innerText = grav.toUpperCase().replace("_", " ");
  if (grav === "urgencia_imediata") gravBadge.className = "pet-badge badge-alert";
  else if (grav === "monitoramento_moderado") gravBadge.className = "pet-badge badge-info";
  else gravBadge.className = "pet-badge badge-ok";

  // Plano (Prescrições)
  const rxTbody = document.getElementById("soapRxTbody");
  if (data.soap.plan.prescricoes_farmacologicas.length > 0) {
    rxTbody.innerHTML = data.soap.plan.prescricoes_farmacologicas.map(rx => `
      <tr>
        <td><strong>${rx.nome_comercial || rx.principio_ativo}</strong><br><small style="color:#64748b;">${rx.forma_farmaceutica}</small></td>
        <td>${rx.dosagem}</td>
        <td>${rx.frequencia_horas ? `A cada ${rx.frequencia_horas}h` : "-"}</td>
        <td>${rx.duracao_dias ? `${rx.duracao_dias} dias` : "-"}</td>
        <td><span class="pet-badge badge-info">${rx.via}</span></td>
      </tr>
    `).join("");
  } else {
    rxTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Nenhum medicamento prescrito.</td></tr>`;
  }

  // Exames
  const examesList = document.getElementById("soapExames");
  examesList.innerHTML = data.soap.plan.exames_solicitados
    .map(e => `<li>${e}</li>`)
    .join("");

  const retorno = data.soap.plan.retorno_agendado_dias;
  document.getElementById("soapRetorno").innerText = retorno ? `${retorno} dias` : "Não definido na consulta";

  // 2. Alertas Clínicos
  const alertContainer = document.getElementById("alertsContainer");
  const alertCountBadge = document.getElementById("alertCountBadge");
  alertCountBadge.innerText = data.alerts.length;

  if (data.alerts.length > 0) {
    alertContainer.innerHTML = data.alerts.map(a => {
      const cls = a.nivel === "perigo_vermelho" ? "alert-danger" : (a.nivel === "alerta_amarelo" ? "alert-warning" : "alert-info");
      const icon = a.nivel === "perigo_vermelho" ? "🚨" : (a.nivel === "alerta_amarelo" ? "⚠️" : "ℹ️");
      return `
        <div class="alert-card ${cls}">
          <div style="font-size: 1.5rem;">${icon}</div>
          <div>
            <strong style="text-transform: uppercase; font-size: 0.8rem;">${a.tipo.replace("_", " ")}</strong>
            <p style="margin-top: 0.2rem; font-size: 0.9rem;">${a.mensagem}</p>
            <small style="opacity: 0.8;">Gatilho: ${a.fator_desencadeante}</small>
          </div>
        </div>
      `;
    }).join("");
  } else {
    alertContainer.innerHTML = `<div style="text-align: center; color: #166534; padding: 2rem;">✅ Nenhum alerta ou contraindicação detectada. Prescrição segura!</div>`;
  }

  // 3. Visão do Tutor (WhatsApp)
  document.getElementById("waSaudacao").innerText = data.tutor_guide.saudacao;
  document.getElementById("waDoenca").innerText = data.tutor_guide.o_que_o_pet_tem;
  
  const waRemedios = document.getElementById("waRemedios");
  waRemedios.innerHTML = data.tutor_guide.cronograma_medicamentos.map(m => `
    <div style="background: #f8fafc; border-left: 3px solid #10b981; padding: 0.5rem; margin-bottom: 0.4rem; border-radius: 4px;">
      <strong>💊 ${m.remedio}</strong><br>
      <small style="color: #334155;">${m.como_dar}</small><br>
      <span style="color: #0369a1; font-weight: 600; font-size: 0.8rem;">⏰ Horários: ${m.horarios_sugeridos.join(" e ")}</span> • 
      <span style="color: #64748b; font-size: 0.75rem;">${m.duracao}</span>
    </div>
  `).join("");

  const waAlertas = document.getElementById("waAlertas");
  waAlertas.innerHTML = data.tutor_guide.sinais_de_alerta.map(s => `<li>${s}</li>`).join("");
  document.getElementById("waProximoPasso").innerHTML = `<strong>📅 Próximo Passo:</strong> ${data.tutor_guide.proximo_passo}`;

  // 4. Gestão da Clínica
  const clinicTbody = document.getElementById("clinicItemsTbody");
  const clinicRec = data.clinic_recommendations;
  if (clinicRec.itens_faturaveis_sugeridos.length > 0) {
    clinicTbody.innerHTML = clinicRec.itens_faturaveis_sugeridos.map(it => `
      <tr>
        <td><strong>${it.item}</strong><br><small style="color:#64748b;">${it.justificativa_clinica}</small></td>
        <td><span class="pet-badge badge-info">${it.categoria}</span></td>
        <td style="color:#059669; font-weight:700;">R$ ${it.valor_estimado_reais.toFixed(2).replace(".", ",")}</td>
      </tr>
    `).join("");
  } else {
    clinicTbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">Nenhum item sugerido.</td></tr>`;
  }
  document.getElementById("clinicTotalValue").innerText = `R$ ${clinicRec.valor_total_potencial_reais.toFixed(2).replace(".", ",")}`;

  const clinicActions = document.getElementById("clinicActionsList");
  clinicActions.innerHTML = clinicRec.acoes_de_fidelizacao.map(a => `<li style="margin-bottom: 5px;">${a}</li>`).join("");

  // 5. Transcrição ASR
  document.getElementById("rawTranscriptText").innerText = data.raw_transcript;
}
