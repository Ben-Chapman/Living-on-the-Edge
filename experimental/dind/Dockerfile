FROM docker:dind

RUN apk add --no-cache py3-pip sysbench
RUN python3 -m venv ~/virtualenvs/dind \
  && source ~/virtualenvs/dind/bin/activate \
  && pip install docker requests

COPY --chmod=755 sysbench.sh .
COPY --chmod=755 dind.py .

# ENTRYPOINT ["./sysbench.sh"]
