FROM python:3.11-slim

# Installiere die benötigten Abhängigkeiten für psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# installiere die benötigten Abhängigkeiten/Dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN python -m pip install --upgrade pip

# Kopiere die relevanten Dateien
COPY . .

EXPOSE 3001  

# Entrypoint hat den Vorteil dass im Vergleich zu CMD Argument Forwarding erlaubt ist
    # Docker Bsp:
        # docker build -t python-app .
        # docker run python-app "./pfad/zur/config.yml"
    # Docker Compose Bsp:
        # services:
          # my-python-service:
            # build: ./pfad/zum/Dockerfile
            # container_name: python-app
            # volumes:
                # - ./pfad/zur/config.yml:/app/config.yml  # Falls die Datei extern liegt
            # command: ["./pfad/zur/config.yml", "weitere_argumente"]
ENTRYPOINT ["python", "bridge_mqtt_data_to_db_local.py", "config.json"]