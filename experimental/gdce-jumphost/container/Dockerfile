# Copyright 2024 Google. This software is provided as-is, without warranty or
# representation for any use or purpose. Your use of it is subject to your agreement
# with Google.

FROM alpine:latest

# If this username is changed, update the username to match in the Helm values.yaml file
# and update the username in container_files/sshd_config
ARG JUMPHOST_USERNAME=jump
ARG JUMPHOST_HOMEDIR=/home/$JUMPHOST_USERNAME

# For the latest stable version:
# kubectl: curl -Ls https://dl.k8s.io/release/stable.txt
# virtctl: curl https://storage.googleapis.com/kubevirt-prow/release/kubevirt/kubevirt/stable.txt
ARG KUBECTL_VERSION=1.31.0
ARG VIRTCTL_VERSION=1.3.1

# Install some useful packages including:
# ISC DNS tools (bind-tools)
# mtr network diagnostic tool (mtr)
# ZSH (Alpine ships with sh, installing a more full-featured shell - zsh)
RUN apk add --no-cache \
  bind-tools \
  curl \
  git \
  iputils \
  mtr \
  openssh \
  openssh-server \
  tmux \
  tzdata \
  vim \
  zsh

# Install a pinned version of kubectl and KubeVirt virtctl
RUN curl -LO https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl \
  && curl -L -o kubectl-virt https://github.com/kubevirt/kubevirt/releases/download/v${VIRTCTL_VERSION}/virtctl-v${VIRTCTL_VERSION}-linux-amd64 \
  && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
  && install -o root -g root -m 0755 kubectl-virt /usr/local/bin/kubectl-virt

# Add a non-root user ($JUMPHOST_USERNAME) and set a random password. The password is not
# used but is required to enable SSH login.
RUN adduser \
  --gecos "K8s Jump Pod" \
  --shell /bin/zsh \
  --uid 500 \
  --disabled-password \
  $JUMPHOST_USERNAME \
  # Set a password derived from /dev/urandom
  && P=$(head -c 32 /dev/urandom | base64); echo -e "${P}\n${P}" | passwd $JUMPHOST_USERNAME


# Generate ssh host keys
RUN ssh-keygen -A

# Symlink vi to vim, create a .ssh directory and recursively chown the home directory
RUN ln -fs /usr/bin/vim /usr/bin/vi \
  && mkdir -m 700 $JUMPHOST_HOMEDIR/.ssh \
  && ln -s -f $JUMPHOST_HOMEDIR/.zshrc $JUMPHOST_HOMEDIR/.zshenv \
  && chown -R $JUMPHOST_USERNAME:$JUMPHOST_USERNAME $JUMPHOST_HOMEDIR

# Copy in our sshd configurations
COPY container_files/sshd_config /etc/ssh/sshd_config
COPY container_files/jumphost_sshd_config /etc/ssh/sshd_config.d/jump.conf

# Enable a customized ZSH profile
COPY --chown=$JUMPHOST_USERNAME:$JUMPHOST_USERNAME container_files/zshrc $JUMPHOST_HOMEDIR/.zshrc

# Enable a reasonable default Vim config
COPY --chown=$JUMPHOST_USERNAME:$JUMPHOST_USERNAME container_files/vimrc $JUMPHOST_HOMEDIR/.vimrc

# Message of the day, presented when logging into this container
COPY container_files/motd /etc/motd

# Initial kubeconfig file
COPY --chown=$JUMPHOST_USERNAME:$JUMPHOST_USERNAME container_files/kube_config $JUMPHOST_HOMEDIR/.kube/config

# sshd has been configured to listen on TCP/22 (the default config)
EXPOSE 22/tcp

# -D -> sshd runs in the foreground, -e -> send output to stderr instead of the system log
CMD ["/usr/sbin/sshd", "-De"]
