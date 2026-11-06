# UNTESTED: written without a Docker daemon in the build environment (FAILURE_MODES F-16).
# Runs the whole lab (harness as root, agent as labagent) inside one container with no network
# for the agent. The harness needs network for model APIs, so for live runs prefer enforced mode on a
# Linux VM, or run a local model server reachable only from the harness.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends util-linux && rm -rf /var/lib/apt/lists/* \
 && useradd --system --no-create-home --shell /usr/sbin/nologin labagent \
 && pip install --no-cache-dir pytest
WORKDIR /lab
COPY . /lab
CMD ["bash", "scripts/verify.sh"]
