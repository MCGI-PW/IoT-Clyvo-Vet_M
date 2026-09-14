"""
Script de Inicialização Universal do ClyvoScribe AI (CLYVO VET).
Suporta execução com Uvicorn/FastAPI (se instalado) ou através do servidor HTTP
nativo do Python com ZERO dependências externas.
"""
import sys
import json
import logging
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Adiciona o diretório raiz ao PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.config import APP_TITLE, APP_VERSION, WEB_DIR
from app.services.pipeline import clyvoscribe_pipeline
from app.services.asr_service import asr_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ClyvoServer")


class NativeClyvoHandler(BaseHTTPRequestHandler):
    """
    Manipulador HTTP nativo da biblioteca padrão do Python.
    Permite rodar todo o sistema e a interface web sem precisar instalar nenhum pacote externo.
    """

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Rotas da API REST
        if path == "/api/health":
            self._send_json({
                "status": "online",
                "service": APP_TITLE,
                "version": APP_VERSION,
                "server": "Python Native Standard HTTP (Zero Dependencies)"
            })
            return

        if path == "/api/pets":
            self._send_json(clyvoscribe_pipeline.list_all_pets())
            return

        if path.startswith("/api/pets/"):
            pet_id = path.replace("/api/pets/", "").strip()
            try:
                pet = clyvoscribe_pipeline.get_pet_profile(pet_id)
                self._send_json(pet.model_dump())
            except Exception as e:
                self._send_error(404, str(e))
            return

        if path == "/api/cases":
            self._send_json(asr_service.list_available_cases())
            return

        # 2. Arquivos Estáticos da Interface Web
        if path in ("/", "/index.html"):
            file_path = WEB_DIR / "index.html"
        else:
            rel_name = path.replace("/static/", "").lstrip("/")
            file_path = WEB_DIR / rel_name

        if file_path.exists() and file_path.is_file():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime_type or "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_error(404, f"Arquivo '{path}' não encontrado.")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        if path == "/api/consultations/process":
            try:
                payload = json.loads(post_body.decode("utf-8"))
                pet_id = payload.get("pet_id", "PET-8921")
                sample_case_id = payload.get("sample_case_id")
                custom_transcript = payload.get("custom_transcript")

                result = clyvoscribe_pipeline.run_consultation_pipeline(
                    pet_id=pet_id,
                    sample_case_id=sample_case_id,
                    custom_transcript=custom_transcript
                )
                self._send_json(result.model_dump())
            except Exception as e:
                logger.error(f"Erro no processamento: {e}")
                self._send_error(400, str(e))
            return

        if path == "/api/consultations/finalize":
            try:
                payload = json.loads(post_body.decode("utf-8"))
                self._send_json({
                    "status": "sucesso",
                    "consultation_id": payload.get("consultation_id"),
                    "mensagem": "Prontuário assinado digitalmente com sucesso pelo Médico-Veterinário!"
                })
            except Exception as e:
                self._send_error(400, str(e))
            return

        self._send_error(404, "Rota POST não encontrada.")

    def _send_json(self, data: any, status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code: int, message: str):
        self._send_json({"error": message, "code": code}, status_code=code)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))


def run(port: int = 8000):
    # Tenta rodar via FastAPI + Uvicorn se instalado
    try:
        import uvicorn
        import fastapi
        logger.info("⚡ Iniciando servidor via FastAPI + Uvicorn...")
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
        return
    except ImportError:
        pass

    logger.info("=" * 65)
    logger.info(f"🐾 CLYVO VET — ClyvoScribe AI iniciado com sucesso!")
    logger.info(f"🌐 Acesse a aplicação no seu navegador: http://localhost:{port}")
    logger.info("💡 Modo de execução nativo ativado (Zero Dependências externas)")
    logger.info("=" * 65)
    server = HTTPServer(("0.0.0.0", port), NativeClyvoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário.")
        server.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run(port)
