FROM python:3.9-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    wget \
    xvfb \
    chromium \
    chromium-driver \
    fonts-liberation \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Installer wkhtmltopdf (optionnel - l'application fonctionnera même sans)
# On utilise une méthode plus simple avec les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    libjpeg62-turbo \
    xfonts-75dpi \
    xfonts-base \
    && wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb -O /tmp/wkhtmltopdf.deb || echo "wkhtmltopdf: téléchargement échoué" && \
    if [ -f /tmp/wkhtmltopdf.deb ]; then \
        dpkg -i /tmp/wkhtmltopdf.deb || apt-get install -yf || echo "wkhtmltopdf: installation échouée, continuons"; \
        rm -f /tmp/wkhtmltopdf.deb; \
    fi && \
    rm -rf /var/lib/apt/lists/*

# Définir les variables d'environnement pour Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99

WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY *.json /app/
COPY *.html /app/
COPY *.txt /app/

# Créer les dossiers nécessaires avec les bonnes permissions
RUN mkdir -p /app/cvs /app/data && \
    chmod -R 777 /app

# Définir le PYTHONPATH pour que les imports fonctionnent
ENV PYTHONPATH=/app/src

# Exposer le port
EXPOSE 2020

# Commande de démarrage
CMD ["python", "-m", "src.app"]
