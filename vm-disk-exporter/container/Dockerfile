FROM alpine:latest

RUN apk add --no-cache \
  bash \
  libnbd \
  openssh \
  rclone \
  rsync \
  qemu-img

WORKDIR /root

COPY files/vm-disk-export.sh .
COPY files/motd /etc/

RUN echo "/etc/motd" >> .bashrc

ENTRYPOINT ["sleep", "infinity"]
