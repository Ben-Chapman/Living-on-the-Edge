FROM alpine:latest as builder

ARG GUACAMOLE_VERSION=1.5.5

RUN apk add curl && \
  mkdir packages && \
  curl -L -o - https://apache.org/dyn/closer.lua/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-quickconnect-${GUACAMOLE_VERSION}.tar.gz?action=download | tar zxvf - && \
  cp guacamole-auth-quickconnect-${GUACAMOLE_VERSION}/guacamole-auth-quickconnect-${GUACAMOLE_VERSION}.jar ./packages/


FROM guacamole/guacamole as runtime
ARG CUSTOM_EXTENSIONS_DIR=/tmp/custom-extensions/extensions
# ARG CUSTOM_EXTENSIONS_DIR=/tmp/

RUN mkdir -p ${CUSTOM_EXTENSIONS_DIR} && chown 1001:1001 ${CUSTOM_EXTENSIONS_DIR}

COPY --chown=1001:1001 --from=builder packages/* ${CUSTOM_EXTENSIONS_DIR}/
