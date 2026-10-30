"""
Configurações da aplicação ClyvoScribe AI (CLYVO VET).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
DOCS_DIR = BASE_DIR / "docs"
WEB_DIR = BASE_DIR / "app" / "web"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLYVO_IA_MODEL = os.getenv("CLYVO_IA_MODEL", "claude-opus-5-5")
APP_TITLE = "ClyvoScribe AI - Inteligência Clínica Veterinária"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

DEFAULT_VET_CRMV = "CRMV-SP 45.892 (Dr. Veterinário Responsável)"
DEFAULT_CLINIC_NAME = "CLYVO VET Hospital & Centro de Especialidades"
