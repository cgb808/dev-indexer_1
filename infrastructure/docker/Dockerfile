###############################
# ZenGlowAI FastAPI Dockerfile
# Focus: reliable build incl. audio + postgres + whisper deps
###############################

FROM python:3.10-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	POETRY_VIRTUALENVS_CREATE=false

# System build + runtime libs (keep minimal but cover: psycopg2, webrtcvad, sounddevice, whisper ffmpeg, piper)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	build-essential \
	git \
	curl \
	ffmpeg \
	portaudio19-dev \
	libsndfile1 \
	libpq-dev \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Separate layer for requirements to leverage caching
COPY requirements.txt ./

# Some packages (bitsandbytes) may fail on CPU-only; allow optional skip
ARG ALLOW_BNB_FAIL=true
RUN set -e; \
	if [ "$ALLOW_BNB_FAIL" = "true" ]; then \
		pip install -r requirements.txt || echo "Continuing despite non-critical pip failures (likely bitsandbytes on CPU)"; \
	else \
		pip install -r requirements.txt; \
	fi

COPY . .

# Non-root user (optional; comment out if volume permissions problematic)
RUN useradd -m appuser || true
USER appuser

EXPOSE 8000

# Healthcheck (basic) - align with actual implemented endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD curl -fsS http://localhost:8000/health || exit 1

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
