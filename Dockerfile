# AuroraScribe AI: serviço de IA da Aurora Pet, sem root
# Roda no servidor nativo do Python (run_server.py); o SDK do Claude entra para quando houver ANTHROPIC_API_KEY
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir anthropic \
    && useradd --create-home --uid 1001 aurora

COPY --chown=aurora:aurora run_server.py ./
COPY --chown=aurora:aurora app ./app
COPY --chown=aurora:aurora samples ./samples

USER aurora
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["python", "run_server.py", "8000"]
