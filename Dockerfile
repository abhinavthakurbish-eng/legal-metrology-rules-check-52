# Production Dockerfile for Render (Zero-Defect Deployment)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=10000

# Install Tesseract OCR & required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Auto-detect tessdata path and set TESSDATA_PREFIX dynamically
RUN TESS_VERSION=$(tesseract --version 2>&1 | grep "^tesseract" | awk '{print $2}' | cut -d. -f1) && \
    echo "Tesseract major version: $TESS_VERSION" && \
    FOUND_PATH="" && \
    for p in \
      "/usr/share/tesseract-ocr/${TESS_VERSION}/tessdata" \
      "/usr/share/tesseract-ocr/4.00/tessdata" \
      "/usr/share/tesseract-ocr/5/tessdata" \
      "/usr/share/tessdata" \
      "/usr/local/share/tessdata"; do \
      if [ -f "${p}/eng.traineddata" ]; then \
        FOUND_PATH="$p"; \
        break; \
      fi; \
    done && \
    echo "Found tessdata at: $FOUND_PATH" && \
    echo "export TESSDATA_PREFIX=$FOUND_PATH" >> /etc/profile.d/tesseract.sh && \
    echo "TESSDATA_PREFIX=$FOUND_PATH" >> /etc/environment && \
    echo "Verified: $(ls $FOUND_PATH/eng.traineddata)"

# Verify Tesseract works
RUN tesseract --version && tesseract --list-langs

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure all runtime folders exist
RUN mkdir -p uploads generated_reports static/annotated static/samples database tessdata

# Set TESSDATA_PREFIX at runtime by finding it dynamically in entrypoint
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'FOUND=""' >> /app/start.sh && \
    echo 'for p in "/usr/share/tesseract-ocr/4.00/tessdata" "/usr/share/tesseract-ocr/5/tessdata" "/usr/share/tessdata" "/usr/local/share/tessdata"; do' >> /app/start.sh && \
    echo '  if [ -f "${p}/eng.traineddata" ]; then FOUND="$p"; break; fi' >> /app/start.sh && \
    echo 'done' >> /app/start.sh && \
    echo 'export TESSDATA_PREFIX="$FOUND"' >> /app/start.sh && \
    echo 'echo "Using TESSDATA_PREFIX=$TESSDATA_PREFIX"' >> /app/start.sh && \
    echo 'exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - app:app' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose Render standard port
EXPOSE 10000

# Use startup script that sets TESSDATA_PREFIX dynamically before gunicorn starts
CMD ["/app/start.sh"]
