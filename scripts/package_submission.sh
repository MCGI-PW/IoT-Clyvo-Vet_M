#!/usr/bin/env bash
# Script para empacotamento do entregável CLYVO VET em arquivo .zip limpo e auditado.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ZIP_NAME="CLYVO_VET_ENTREGA_IA.zip"
OUTPUT_PATH="$PROJECT_ROOT/$ZIP_NAME"

echo "=========================================================="
echo "📦 Gerando arquivo de entrega oficial da CLYVO VET..."
echo "=========================================================="

# Remove zip anterior se existir
if [ -f "$OUTPUT_PATH" ]; then
    rm "$OUTPUT_PATH"
    echo "🧹 Arquivo anterior removido."
fi

# Navega até o diretório pai para empacotar a pasta do projeto
cd "$PROJECT_ROOT/.."

# Cria o zip ignorando arquivos temporários e caches
zip -r "$OUTPUT_PATH" clyvo-vet-ai \
    -x "*/__pycache__/*" \
    -x "*/.pytest_cache/*" \
    -x "*/.DS_Store" \
    -x "*.pyc" \
    -x "*/.git/*" \
    -x "*/.venv/*" \
    -x "*/node_modules/*"

echo "=========================================================="
echo "✅ Arquivo gerado com sucesso em:"
echo "   $OUTPUT_PATH"
echo ""
echo "📊 Verificação de integridade do .zip:"
unzip -t "$OUTPUT_PATH" | tail -n 2
echo "=========================================================="
