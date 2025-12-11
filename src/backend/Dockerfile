FROM python:3.10-slim-bookworm

# 1. Install System Deps (Cached Layer)
# We combine updates into one line to reduce image layers
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python Deps (Cached Layer)
# Docker will ONLY re-run this if requirements.txt changes.
# If you just change main.py, this step is SKIPPED (saving 45+ mins).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Pre-load Whisper Model (Cached Layer)
# This prevents the model download from happening at runtime or re-build.
RUN python -c "import whisper; whisper.load_model('base')"

# 4. Copy Code (Frequent Changes)
# This is the only step that re-runs when you edit your code.
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]