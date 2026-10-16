FROM python:3.12.14-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONUTF8=1 PROJECT_ROOT=/workspace PREFECT_HOME=/home/app/.prefect
WORKDIR /workspace/backend
COPY backend/requirements.txt backend/runtime-constraints.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt -c /tmp/runtime-constraints.txt
RUN useradd --create-home --uid 10001 app
RUN mkdir /home/app/research-assets && chown app:app /home/app/research-assets
COPY --chown=app:app backend /workspace/backend
COPY --chown=app:app industry-map /workspace/industry-map
COPY --chown=app:app data /workspace/data
COPY --chown=app:app scripts/validate_map.py /workspace/scripts/validate_map.py
COPY --chown=app:app scripts/research_schema.py /workspace/scripts/research_schema.py
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
