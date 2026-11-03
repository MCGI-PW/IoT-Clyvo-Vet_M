# ClyvoScribe AI: serviço de IA da CLYVO VET, sem root
# Roda no servidor nativo do Python (run_server.py); o SDK do Claude entra para quando houver ANTHROPIC_API_KEY
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir anthropic \
    && useradd --create-home --uid 1001 clyvo

COPY --chown=clyvo:clyvo run_server.py ./
COPY --chown=clyvo:clyvo app ./app
COPY --chown=clyvo:clyvo samples ./samples

USER clyvo
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["python", "run_server.py", "8000"]
