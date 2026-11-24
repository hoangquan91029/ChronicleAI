FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including fontconfig for Vietnamese Unicode rendering in PDFs and FFmpeg for video rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    fonts-liberation \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate sample documents if not already present
RUN python sample_data/generate_sample_pdf.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
