# Runtime template for HF Docker Space (requires eligible compute plan) or Oracle.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg espeak-ng ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gradio==5.49.1
COPY shortgpt_supertest.py ./
COPY huggingface_space/app.py ./app.py
RUN useradd -m -u 1000 app && mkdir -p /app/output && chown -R app:app /app
USER app
EXPOSE 7860
CMD ["python","app.py"]
