############################################################
# Slim Indexer Image (no XRDP / desktop)                    #
# Keep minimal; add system deps only when actually needed.  #
############################################################
FROM python:3.12-slim AS base

# ---------------------------------------------------------
# Build-time arguments to align container user with host
# Override with: --build-arg UID=$(id -u) --build-arg GID=$(id -g)
# USERNAME defaults to cgb808 (development identity)
# ---------------------------------------------------------
ARG UID=1000
ARG GID=1000
ARG USERNAME=cgb808

ENV PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	DEBIAN_FRONTEND=noninteractive \
	APP_HOME=/workspace \
	HOME=/home/${USERNAME}

WORKDIR ${APP_HOME}

# System deps: build essentials (future native libs) + minimal tooling.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	curl ca-certificates git build-essential procps sudo \
	&& groupadd -g ${GID} ${USERNAME} \
	&& useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME} \
	&& usermod -aG sudo ${USERNAME} \
	&& echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-${USERNAME} \
	&& chmod 440 /etc/sudoers.d/90-${USERNAME} \
	&& mkdir -p /home/${USERNAME}/.cache/pip /home/${USERNAME}/.cache/uv /home/${USERNAME}/.local/bin \
	&& chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.cache /home/${USERNAME}/.local \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# Copy only requirements early for layer caching (requirements file intentionally minimal per project policy).
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application source (keep broad; rely on .dockerignore if added later).
COPY app ./app
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

USER root

# Expose RDP + API; run both xrdp and app via start script
USER ${USERNAME}

ENTRYPOINT ["/usr/local/bin/start.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
