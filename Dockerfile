# Sprint 9 (C-06): imagen reproducible. FFmpeg vía apt (adiós bin/ de 300 MB).
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py config.py aliases.example.json trolls.example.json ./
COPY core/ core/
COPY music/ music/
COPY ui/ ui/
COPY utils/ utils/

# El token llega por entorno (compose env_file), nunca en la imagen.
CMD ["python", "bot.py"]
