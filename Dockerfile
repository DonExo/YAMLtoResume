FROM python:3.12-slim

# DejaVu fonts (for Unicode symbols in the PDF contact line)
RUN apt-get update && apt-get install -y --no-install-recommends \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure static dir exists so default.png mount works even if folder is absent
RUN mkdir -p static

EXPOSE 5000

CMD ["python", "app.py"]
