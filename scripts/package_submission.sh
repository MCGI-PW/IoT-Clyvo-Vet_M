#!/usr/bin/env bash
# Gera o .zip da entrega de IA (Sprint 4): código versionado + ENTREGA.txt com os links.
# Uso: bash scripts/package_submission.sh "https://youtu.be/LINK_DO_VIDEO"

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASTA="$(basename "$PROJECT_ROOT")"
ZIP_NAME="CLYVO_VET_ENTREGA_IA.zip"
OUTPUT_PATH="$PROJECT_ROOT/$ZIP_NAME"
REPO_URL="https://github.com/MCGI-PW/IoT-Clyvo-Vet_M"
VIDEO_URL="${1:-}"

if [ -z "$VIDEO_URL" ]; then
    echo "⚠️  Informe o link do vídeo no YouTube: bash scripts/package_submission.sh \"https://youtu.be/...\"" >&2
    exit 1
fi

cd "$PROJECT_ROOT"
rm -f "$OUTPUT_PATH"

# Só os arquivos versionados no Git: sem caches, .env ou arquivos locais
git archive --format=zip --prefix="$PASTA/" -o "$OUTPUT_PATH" HEAD

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
cat > "$TMP_DIR/ENTREGA.txt" <<TXT
CLYVO VET - ClyvoScribe AI
Disruptive Architectures: IoT, IoB & Generative IA - Sprint 4

Vídeo (YouTube, não listado): $VIDEO_URL
Repositório no GitHub:        $REPO_URL

Integrantes:
  Maicon Douglas  RM561279
  Gabriel F.      RM561551
  Charlles        RM566482
  Iago D.         RM565708

Como executar: python3 run_server.py (http://localhost:8000). Instruções completas no README.md.
TXT
(cd "$TMP_DIR" && zip -q "$OUTPUT_PATH" ENTREGA.txt)

echo "✅ Gerado: $OUTPUT_PATH"
unzip -l "$OUTPUT_PATH" | tail -n 1
unzip -tq "$OUTPUT_PATH"
