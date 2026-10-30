"""
Extração do prontuário SOAP com IA generativa (Claude, da Anthropic).
Usa saída estruturada (JSON Schema): a resposta já chega no formato do SOAPRecord.
É opcional: sem o pacote `anthropic` ou sem ANTHROPIC_API_KEY, o pipeline usa o extrator local.
"""
import json
import logging
from typing import Any, Dict, Optional

from app.config import ANTHROPIC_API_KEY, CLYVO_IA_MODEL
from app.models.pet import PetHealthProfile

logger = logging.getLogger(__name__)

PROMPT_SISTEMA = """Você é um assistente de documentação clínica veterinária da CLYVO VET.
Recebe a transcrição de uma consulta entre veterinário e tutor e organiza o prontuário no padrão SOAP.

Regras obrigatórias:
- Use somente o que foi dito na consulta. Não invente diagnóstico, medicamento, dose, exame, sinal vital ou prazo.
- Campo sem informação na conversa: texto vazio, lista vazia ou null.
- Hipóteses diagnósticas só quando o veterinário disser ou sugerir claramente.
- frequencia_horas é o intervalo entre doses (ex.: "duas vezes ao dia" = 12); duracao_dias é o total de dias do tratamento.
- resumo_tutor: 2 a 4 frases simples e acolhedoras para o tutor, sem termos técnicos.
- sinais_alerta: situações citadas na consulta que exigem voltar à clínica ou procurar emergência.
- Escreva em português do Brasil."""


def _texto(descricao: str) -> Dict[str, Any]:
    return {"type": "string", "description": descricao}


def _lista_texto(descricao: str) -> Dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}, "description": descricao}


def _opcional(tipo: str) -> Dict[str, Any]:
    return {"anyOf": [{"type": tipo}, {"type": "null"}]}


def _objeto(propriedades: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": propriedades,
        "required": list(propriedades.keys()),
        "additionalProperties": False,
    }


# Espelha app/models/consultation.py (SOAPRecord) para a resposta já chegar validada
SOAP_SCHEMA = _objeto({
    "subjective": _objeto({
        "queixa_principal": _texto("Queixa principal relatada pelo tutor"),
        "historico_molestia_atual": _texto("Histórico da queixa atual"),
        "alimentacao_e_apetite": _opcional("string"),
        "comportamento_e_rotina": _opcional("string"),
    }),
    "objective": _objeto({
        "parametros_vitais": _objeto({
            "temperatura_retal_c": _opcional("number"),
            "frequencia_cardiaca_bpm": _opcional("integer"),
            "frequencia_respiratoria_mpm": _opcional("integer"),
            "tempo_preenchimento_capilar_seg": _opcional("integer"),
            "grau_desidratacao_pct": _opcional("integer"),
        }),
        "exame_fisico_geral": _texto("Achados gerais do exame físico citados"),
        "exame_fisico_especifico": _texto("Achados específicos do exame físico citados"),
    }),
    "assessment": _objeto({
        "hipoteses_diagnosticas": _lista_texto("Hipóteses diagnósticas ditas pelo veterinário"),
        "nivel_gravidade": {
            "type": "string",
            "enum": ["rotina_estavel", "monitoramento_moderado", "urgencia_imediata"],
        },
    }),
    "plan": _objeto({
        "exames_solicitados": _lista_texto("Exames pedidos na consulta"),
        "prescricoes_farmacologicas": {
            "type": "array",
            "items": _objeto({
                "principio_ativo": _texto("Medicamento citado"),
                "nome_comercial": _opcional("string"),
                "forma_farmaceutica": _texto("Gotas, comprimido, pomada etc."),
                "dosagem": _texto("Dose dita na consulta"),
                "frequencia_horas": _opcional("integer"),
                "duracao_dias": _opcional("integer"),
                "via": _texto("Via de administração"),
                "instrucoes_especiais": _opcional("string"),
            }),
        },
        "recomendacoes_manejo": _lista_texto("Orientações de cuidado em casa"),
        "retorno_agendado_dias": _opcional("integer"),
    }),
    "resumo_tutor": _texto("Resumo em linguagem simples para o tutor"),
    "sinais_alerta": _lista_texto("Sinais que exigem voltar à clínica"),
})


def _sem_nulos(valor: Any) -> Any:
    """Remove chaves nulas para que os modelos apliquem seus próprios valores padrão."""
    if isinstance(valor, dict):
        return {k: _sem_nulos(v) for k, v in valor.items() if v is not None}
    if isinstance(valor, list):
        return [_sem_nulos(v) for v in valor]
    return valor


class ClaudeSoapExtractor:
    def __init__(self, api_key: str = ANTHROPIC_API_KEY, model: str = CLYVO_IA_MODEL, client: Any = None):
        self.model = model
        self._client = client
        if self._client is None and api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                logger.warning("ANTHROPIC_API_KEY definida, mas o pacote 'anthropic' não está instalado (pip install anthropic).")

    @property
    def disponivel(self) -> bool:
        return self._client is not None

    @property
    def fonte(self) -> str:
        return f"CLAUDE:{self.model}"

    def extrair(self, transcricao: str, pet: PetHealthProfile) -> Dict[str, Any]:
        """Devolve o SOAP como dicionário. Lança RuntimeError se a IA não puder responder."""
        if not self.disponivel:
            raise RuntimeError("Claude não configurado.")

        # LGPD: vai só o necessário do paciente; dados do tutor ficam de fora
        contexto = f"Paciente: {pet.nome}, {pet.especie}, raça {pet.raca or 'não informada'}."
        response = self._client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=PROMPT_SISTEMA,
            messages=[{
                "role": "user",
                "content": f"{contexto}\n\n<transcricao>\n{transcricao}\n</transcricao>",
            }],
            output_config={"format": {"type": "json_schema", "schema": SOAP_SCHEMA}},
        )

        if response.stop_reason == "refusal":
            raise RuntimeError("Claude recusou a solicitação.")
        if response.stop_reason == "max_tokens":
            raise RuntimeError("Resposta do Claude truncada.")

        texto: Optional[str] = next((b.text for b in response.content if b.type == "text"), None)
        if not texto:
            raise RuntimeError("Claude não retornou conteúdo.")
        return _sem_nulos(json.loads(texto))


claude_extractor = ClaudeSoapExtractor()
