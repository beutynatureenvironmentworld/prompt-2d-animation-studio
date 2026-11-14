FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY studio ./studio
COPY examples ./examples
RUN mkdir -p output assets/audio assets/references
ENTRYPOINT ["python", "-m", "studio.automatic"]
CMD ["bedroom two stick figures snore"]
