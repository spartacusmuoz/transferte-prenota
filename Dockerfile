# Usa un'immagine base leggera di Python 3.11
FROM python:3.11-slim

# Imposta la cartella di lavoro dentro il container
WORKDIR /app

# Copia il file requirements e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del progetto nella cartella di lavoro
COPY . .

# Espone la porta su cui Uvicorn girerà
EXPOSE 8000

# Comando per avviare Uvicorn quando il container parte
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
