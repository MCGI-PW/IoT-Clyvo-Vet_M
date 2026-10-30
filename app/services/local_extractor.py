"""
Extrator clínico local (sem internet): monta o SOAP a partir das frases reais da transcrição.
Cada frase é classificada por palavras-chave. Nada é inventado: o que não foi dito fica vazio.
É o plano B quando o Claude não está configurado ou falha.
"""
import re
import unicodedata
from typing import List, Optional

from app.models.pet import PetHealthProfile
from app.models.consultation import (
    SOAPRecord, SubjectiveSection, ObjectiveSection, AssessmentSection,
    PlanSection, VitalSigns, PrescriptionItem
)

# Radicais sem acento, comparados com a frase normalizada
QUEIXA = ["cocando", "coceira", "vomit", "diarreia", "manca", "mancando", "dor", "nao quer comer",
          "nao come", "sem apetite", "tosse", "espirr", "sangue", "febre", "triste", "quieto", "quieta",
          "desde", "ha uns", "ha dois", "ha tres", "ha quatro", "chacoalha", "lambendo", "cheiro"]
EXAME = ["temperatura", "graus", "mucosa", "palpacao", "palpei", "ausculta", "batimentos", "otoscopia",
         "exame fisico", "hidratad", "desidrat", "linfonodo", "peso", "examinei", "examinando"]
DIAGNOSTICO = ["diagnostico", "suspeita", "parece ser", "parece uma", "trata-se", "quadro de", "compativel",
               "hipotese", "provavel", "provavelmente", "e uma otite", "infeccao", "inflamacao",
               "dermatite", "gastrite", "gastroenterite", "fratura", "luxacao", "alergia"]
PRESCRICAO = ["prescrev", "receitar", "receitei", "vou passar", "medicamento", "remedio", "comprimido",
              "gotas", "pomada", "xarope", "injecao", "antibiotico", "anti-inflamatorio", "mg", "ml"]
EXAMES_PEDIDOS = ["hemograma", "bioquimic", "radiografia", "raio-x", "raio x", "ultrassom", "ultrassonografia",
                  "citologia", "cultura", "urinalise", "exame de sangue", "exame de urina", "raspado"]
ORIENTACAO = ["retorn", "voltar", "volte", "evit", "mantenha", "manter", "repouso", "jejum", "observ",
              "limp", "dieta", "racao", "agua", "colar elizabetano", "nao deixe", "cuidado"]
ALERTA = ["se ele", "se ela", "caso ele", "caso ela", "se tiver", "se apresentar", "procure", "emergencia",
          "imediatamente", "urgente", "piorar"]
URGENCIA = ["internacao", "internar", "emergencia", "urgente", "urgencia", "grave", "risco de vida"]

NUMEROS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
           "sete": 7, "oito": 8, "nove": 9, "dez": 10, "doze": 12, "quinze": 15, "vinte": 20, "trinta": 30}
_NUM = r"(\d+|" + "|".join(NUMEROS) + r")"


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def _numero(token: str) -> int:
    return int(token) if token.isdigit() else NUMEROS[token]


def _contem(frase_norm: str, termos: List[str]) -> bool:
    return any(re.search(r"(?<![a-z])" + re.escape(t), frase_norm) for t in termos)


def _frases(transcricao: str) -> List[str]:
    """Quebra em frases e tira o rótulo do locutor ("Veterinário:", "Tutor:")."""
    frases = []
    for linha in transcricao.splitlines():
        linha = re.sub(r"^\s*(?:Veterin[áa]ri[oa]|Tutora?|M[ée]dic[oa]|Dra?\.?[^:]{0,20})\s*:\s*", "", linha, flags=re.I)
        for frase in re.split(r"(?<=[.!?])\s+", linha):
            frase = frase.strip()
            if len(frase) > 3:
                frases.append(frase)
    return frases


def frequencia_em_horas(frase_norm: str) -> Optional[int]:
    m = re.search(r"a cada " + _NUM + r" ?(?:horas|h)\b", frase_norm)
    if m:
        return _numero(m.group(1))
    m = re.search(_NUM + r" vez(?:es)? (?:ao|por) dia", frase_norm)
    if m:
        vezes = _numero(m.group(1))
        return 24 // vezes if vezes else None
    if "de 12 em 12" in frase_norm:
        return 12
    if "de 8 em 8" in frase_norm:
        return 8
    return None


def duracao_em_dias(frase_norm: str) -> Optional[int]:
    m = re.search(r"(?:por|durante) " + _NUM + r" dias", frase_norm)
    if m:
        return _numero(m.group(1))
    m = re.search(r"(?:por|durante) " + _NUM + r" semanas?", frase_norm)
    return _numero(m.group(1)) * 7 if m else None


def retorno_em_dias(texto_norm: str) -> Optional[int]:
    m = re.search(r"retorno (?:em|daqui a|de) " + _NUM + r" dias", texto_norm)
    if m:
        return _numero(m.group(1))
    m = re.search(r"(?:voltar|volte|retornar) (?:em|daqui a) " + _NUM + r" dias", texto_norm)
    return _numero(m.group(1)) if m else None


def _sinais_vitais(texto_norm: str) -> VitalSigns:
    temp = re.search(r"(\d{2}[.,]\d+)\s*(?:graus|°c|celsius)", texto_norm)
    fc = re.search(r"(\d{2,3})\s*(?:batimentos|bpm)", texto_norm)
    fr = re.search(r"(\d{2,3})\s*(?:movimentos|mpm|respiracoes)", texto_norm)
    return VitalSigns(
        temperatura_retal_c=float(temp.group(1).replace(",", ".")) if temp else None,
        frequencia_cardiaca_bpm=int(fc.group(1)) if fc else None,
        frequencia_respiratoria_mpm=int(fr.group(1)) if fr else None,
        grau_desidratacao_pct=None,
    )


def _via(frase_norm: str) -> str:
    if "gota" in frase_norm and ("orelha" in frase_norm or "ouvido" in frase_norm):
        return "Tópica Auricular"
    if "gota" in frase_norm and "olho" in frase_norm:
        return "Oftálmica"
    if "pomada" in frase_norm or "passar na pele" in frase_norm:
        return "Tópica"
    if "injec" in frase_norm or "injetavel" in frase_norm:
        return "Injetável"
    return "Oral"


def _forma(frase_norm: str) -> str:
    for termo, forma in (("gota", "Gotas"), ("comprimido", "Comprimidos"), ("pomada", "Pomada"),
                         ("xarope", "Xarope"), ("injec", "Injetável"), ("capsula", "Cápsulas")):
        if termo in frase_norm:
            return forma
    return "Conforme orientação"


def _dosagem(frase_norm: str, frase: str) -> str:
    m = re.search(_NUM + r" ?(gotas?|comprimidos?|mg|ml|capsulas?|saches?)", frase_norm)
    return f"{m.group(1)} {m.group(2)}" if m else frase


def _prescricao(frase: str) -> PrescriptionItem:
    norm = normalizar(frase)
    return PrescriptionItem(
        principio_ativo=frase,
        forma_farmaceutica=_forma(norm),
        dosagem=_dosagem(norm, frase),
        frequencia_horas=frequencia_em_horas(norm),
        duracao_dias=duracao_em_dias(norm),
        via=_via(norm),
    )


def extrair_soap(transcricao: str, pet: PetHealthProfile) -> SOAPRecord:
    queixas, exames_fisicos, diagnosticos, prescricoes = [], [], [], []
    exames, orientacoes, alertas = [], [], []

    for frase in _frases(transcricao):
        norm = normalizar(frase)
        # Uma frase pode ser alerta e orientação ao mesmo tempo; as demais categorias são exclusivas
        if _contem(norm, ALERTA):
            alertas.append(frase)
            continue
        if _contem(norm, PRESCRICAO) and (frequencia_em_horas(norm) or duracao_em_dias(norm) or "prescrev" in norm):
            prescricoes.append(_prescricao(frase))
        elif _contem(norm, DIAGNOSTICO):
            diagnosticos.append(frase)
        elif _contem(norm, EXAMES_PEDIDOS):
            exames.append(frase)
        elif _contem(norm, EXAME):
            exames_fisicos.append(frase)
        elif _contem(norm, ORIENTACAO):
            orientacoes.append(frase)
        elif _contem(norm, QUEIXA):
            queixas.append(frase)

    texto_norm = normalizar(transcricao)
    gravidade = "urgencia_imediata" if _contem(texto_norm, URGENCIA) else "monitoramento_moderado"
    diagnostico_txt = "; ".join(diagnosticos)

    resumo_tutor = f"Resumo da consulta do(a) {pet.nome}."
    if diagnostico_txt:
        resumo_tutor += f" O que o(a) veterinário(a) avaliou: {diagnostico_txt}"
    if prescricoes:
        resumo_tutor += f" Foram indicados {len(prescricoes)} medicamento(s); siga os horários abaixo."
    if orientacoes:
        resumo_tutor += " Cuidados em casa: " + " ".join(orientacoes)

    return SOAPRecord(
        subjective=SubjectiveSection(
            queixa_principal=queixas[0] if queixas else "",
            historico_molestia_atual=" ".join(queixas[1:]),
        ),
        objective=ObjectiveSection(
            parametros_vitais=_sinais_vitais(texto_norm),
            exame_fisico_geral=" ".join(exames_fisicos),
            exame_fisico_especifico="",
        ),
        assessment=AssessmentSection(hipoteses_diagnosticas=diagnosticos, nivel_gravidade=gravidade),
        plan=PlanSection(
            exames_solicitados=exames,
            prescricoes_farmacologicas=prescricoes,
            recomendacoes_manejo=orientacoes,
            retorno_agendado_dias=retorno_em_dias(texto_norm),
        ),
        resumo_tutor=resumo_tutor,
        sinais_alerta=alertas,
        fonte_ia="LOCAL:extracao",
    )
