FROM python:3.13-slim AS build

RUN apt-get update && \
  apt-get install -y curl && \
  # Install uv
  curl -LsSf https://astral.sh/uv/install.sh | sh

FROM python:3.13-slim AS run

RUN useradd -m -r -u 1001 dnsmonitor
USER dnsmonitor
WORKDIR /home/dnsmonitor

COPY --chown=dnsmonitor:dnsmonitor --from=build /root/.local/bin/ .local/bin/

ENV PATH="/home/dnsmonitor/.local/bin:$PATH"

COPY --chown=dnsmonitor:dnsmonitor dns_monitor.py pyproject.toml ./

# Install required packages
RUN uv sync

ENTRYPOINT [ "uv", "run", "dns_monitor.py" ]
