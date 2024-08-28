FROM alpine:latest as builder

ARG GUACAMOLE_VERSION=1.5.5

RUN apk add curl && \
  mkdir packages && \
  curl -L -o - https://apache.org/dyn/closer.lua/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-quickconnect-${GUACAMOLE_VERSION}.tar.gz?action=download | tar zxvf - && \
  cp guacamole-auth-quickconnect-${GUACAMOLE_VERSION}/guacamole-auth-quickconnect-${GUACAMOLE_VERSION}.jar ./packages/


FROM guacamole/guacamole as runtime
ARG EXTENSIONS_DIR=/home/guacamole/.guacamole/extensions

RUN mkdir -p ${EXTENSIONS_DIR}
# RUN mkdir /home/guacamole/.guacamole/extensions

COPY --from=builder packages/* ${EXTENSIONS_DIR}
