# Copyright 2024 Google. This software is provided as-is, without warranty or
# representation for any use or purpose. Your use of it is subject to your agreement
# with Google.

FROM alpine:latest

# If this username is changed, update the username to match in the Helm values.yaml file
# and update the username in container_files/sshd_config
ARG JUMPPOD_USERNAME=jump
ARG JUMPPOD_HOMEDIR=/home/$JUMPPOD_USERNAME

ARG KUBECTL_VERSION=1.30.0
ARG VIRTCTL_VERSION=1.2.0

# Install some useful packages including:
# ISC DNS tools (bind-tools)
# mtr network diagnostic tool (mtr)
# ZSH (Alpine ships with sh, installing a more full-featured shell) (zsh)
RUN apk add --no-cache \
  bind-tools \
  curl \
  git \
  iputils \
  mtr \
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

# Add a non-root user ($JUMPPOD_USERNAME) and set a random password. The password is not
# used but is required to enable SSH login.
RUN adduser \
  --gecos "K8s Jump Pod" \
  --shell /bin/zsh \
  --uid 500 \
  $JUMPPOD_USERNAME \
  # Set a password derived from /dev/urandom
  && P=$(head -c 32 /dev/urandom | base64); echo -e "${P}\n${P}" | passwd $JUMPPOD_USERNAME


# Generate ssh host keys, prevent root login through SSH and do not check file modes
# and ownership of sshd-related files before accepting login.
# We're mounting a K8s ConfigMap as a volume in the Pod, and there are limited controls
# within K8s to mount this ConfigMap with the sshd desired dir/file permissions.
# sshd StrictMode was designed to protect permission misconfiguration for user config
# files shared workstations.
# As this is a static and hermetic image this protection isn't as useful, so disabling it.
# For more detail, man sshd
RUN ssh-keygen -A \
  && sed -i -e \
  's/#PermitRootLogin prohibit-password/PermitRootLogin no/g;s/#StrictModes yes/StrictModes no/g' \
  /etc/ssh/sshd_config

# Symlink vi to vim, create a .ssh directory and recursively chown the home directory
RUN ln -fs /usr/bin/vim /usr/bin/vi \
  && mkdir -m 700 $JUMPPOD_HOMEDIR/.ssh \
  && chown -R $JUMPPOD_USERNAME:$JUMPPOD_USERNAME $JUMPPOD_HOMEDIR

# Copy in our sshd customizations for the $JUMPPOD_USERNAME user
COPY container_files/jumphost_sshd_config /etc/ssh/sshd_config.d/jump.conf

# Enable a customized ZSH profile
COPY --chown=$JUMPPOD_USERNAME:$JUMPPOD_USERNAME container_files/zshrc $JUMPPOD_HOMEDIR/.zshrc

# Enable a reasonable default Vim config
COPY --chown=$JUMPPOD_USERNAME:$JUMPPOD_USERNAME container_files/vimrc $JUMPPOD_HOMEDIR/.vimrc

# Message of the day, presented when logging into this container
COPY container_files/motd /etc/motd

# sshd has been configured to listen on TCP/22 (the default config)
EXPOSE 22/tcp

# -D -> sshd runs in the foreground, -e -> send output to stderr instead of the system log
CMD ["/usr/sbin/sshd", "-De"]
