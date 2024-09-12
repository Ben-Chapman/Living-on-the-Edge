# GDCE Jump Host

The GDCE Jump Host (jumphost) is a lightweight container-based SSH bastion host
used to interact with a local cluster's kube-apiserver, primarily through `kubectl`.

This jumphost was designed to use either the GDCE default network or GDCE multinetworks,
and is accessible through a MetalLB VIP or a GDCE secondary (VLAN) network.

## Background

Google Distributed Cloud Edge (GDCE) is a Google-managed on-premise Kubernetes
cluster which is designed to run at the edge of a retail customer's network,
primarily in their stores.

Day-to-day connectivity with the kube-apiserver is facilitated through the
[GCP Connect Gateway](https://cloud.google.com/kubernetes-engine/enterprise/multicluster-management/gateway).
Connect Gateway provides a simple, consistent and secured way to access your
Google-registered Kubernetes clusters regardless of the cluster's physical
location. The vast majority of your interaction with the GDCE clusters will be
through Connect Gateway, but there are a few Kubernetes-related operations that
Connect Gateway does not support today:

- `kubectl exec`
- `kubectl attach`
- `kubectl port-forward`
- `kubectl virt ssh` (Kubevirt)
- `kubectl virt console` (Kubevirt)
- `kubectl virt vnc` (Kubevirt)

These operations are common enough in day-to-day management of Kubernetes workloads that
an alternative solution was developed, and that's the GDCE Jumphost.

## Installation
The GDCE jumphost consists of a custom-built container image; the installation and
management of the jumphost is provided as a Helm package.

### Container Image Build
The container image is based on a standard Alpine Linux base image, with various customizations
to support serving as an SSH-based jumphost. All detail for this image can be found in
the [Dockerfile](container/Dockerfile).

There is nothing novel about the image build process, you just need to build and push the
container image to the image registry of your choice. For example, using GCP Artifact Registry:

```
❯ docker build -t us-central1-docker.pkg.dev/gcp-project/image-repo/gdce-jumphost:latest .

❯ docker push us-central1-docker.pkg.dev/gcp-project/image-repo/gdce-jumphost:latest
```

### Jumphost Installation
Before installing the jumphost, you will need to edit the Helm chart
[values.yaml](helm/values.yaml) updating the various values to match your environment.

One note, the jumphost username `jump` is defined throughout the jumphost configuration
files. If you would like to change this username, search and replace throughout the
config files. Comments have been added in various places to help guide in what needs to
be changed and where.

Once your values have been defined, installation is as simple as
`cd helm; helm install gdce-jumphost ./`

Alternatively if you wish to install through standard Kubernetes manifests:
`cd helm; helm template . | kubectl apply -f -`


## Usage
The GDCE Jump Host will be installed on each GDCE cluster, and consists of a
single Pod running [OpenSSH](https://www.openssh.com/). SSH login access is
provided **only** through public-key authentication; no password-based
authentication is provided or supported.

A Kubernetes ConfigMap containing each user's SSH public key is mounted into the
Pod, and is used to authenticate a user's SSH session.

### Initial Setup
1. Generate an SSH keypair (if needed)
   - Follow the  instructions for your specific workstation OS:
     - [macOS and Linux](https://git-scm.com/book/pt-pt/v2/Git-no-Servidor-Generating-Your-SSH-Public-Key)
     - [Windows](https://learn.microsoft.com/en-us/viva/glint/setup/sftp-ssh-key-gen#create-an-ssh-key-pair-on-microsoft-windows)
2. Add your SSH public key to the ConfigMap
   - Create a new Git branch to stage your config file updates
     - `git checkout -b <new-branch-name>`
   - In your editor of choice, edit [ssh-keys-configmap.yaml](helm/templates/ssh-keys-configmap.yaml)
   adding your email address as a comment, and then your ssh public key. An
   example of this should resemble:

   ```
   # firstname.lastname@domain.com
   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQD2EVP4R+hZ/qoL2+6jy0GoZG61B07lpIpwfKlRxbpuYMj1tsB5GsL0ti8gjlkx1lyc6L9BHbIDCL6UmMzNGRfZVVUPa5ICKTvPm4twaWSqrg+wj0YIV0ch6MVqXXevRg7Tkh6Sb/HlFgSJarOSYE84bqrxjOttusjXIKlOAFZyYHw0zFz0TU4vngqu09NtNMqoFzI0V32qGqOfckJJOf+9xA6extqvxQzOEwZs40gxm7AvzKI61AOn2/zFkBueSdG9+4ymeCM0s7X1idMOm0CYNX3NhYNuvmeTQLhGoVY/+eQ4fGXG8Hh3yOA/dfAdSN68mCSXFUFeFpKAyQj8uiOHIh+s7xELb14IfYE2uF05e5mAgJN3yy0F5XoK2D3Jg7e4RatVGHW0ILTBwZrqEWppUcpTADXIZ2P4gA3/rhlWfFOcRHfKXKqzxqvkjyx46Rmb4Pl8ax1EMH+Hw0+Rxh86ISNHf/j0TbL1BOQClB6NSFT6TDNoh+47GbnKSDts9rc= username@OX901TJ5LWH0GRD
   ```

   - Ensure you **<u>do not</u>** add your private SSH key, which has a first
   line containing `-----BEGIN OPENSSH PRIVATE KEY-----`. This private key
   should remain secured on your workstation.
   - When your public key has been added to the ConfigMap, commit and push your
   changes and create a new Github pull request for peer review.
   - Once the changes have been reviewed, merged and applied to the Cluster you
   now have the ability to log into the jumphost.

### Using the GDCE Jumphost
Once your SSH public key has been applied to the cluster, you can simply `ssh jump@<jumphost-hostname>`

#### Default Network Jumphost IP Address
If you did not define a static MetalLB load-balancer VIP IP address in the Helm values
file, you can determine the IP address allocated by MetalLB through
`kubectl get svc -n gdce-jumphost`.

#### GDCE Multinetwork Jumphost IP Address
If you do not have a standardized hostname or IP address scheme for various
cluster-specific jumphosts, some initial work is needed to determine the IP
address for the jumphost you're looking to connect to.

Using Connect Gateway, run the following command on the cluster hosting the jumphost you
wish to connect to:

`kubectl get pods -n gdce-jumphost -o=jsonpath='{range .items[0]}{.metadata.annotations.networking\.gke\.io/pod-ips}{end}'`

The output from this command will produce detail on the multinetwork-assigned IP
address for this Pod:

```
[{"networkName":"gdce-secondary-network","ip":"10.223.172.245"}]
```

You can now SSH into the jumphost using the IP address assigned to your jumphost:

```
❯ ssh jump@10.223.172.245

                             _______  _______   ______  _______
                            /  _____||       \ /      ||   ____|
                           |  |  __  |  .--.  |  ,----'|  |__
                           |  | |_ | |  |  |  |  |     |   __|
                           |  |__| | |  '--'  |  `----.|  |____
                            \______| |_______/ \______||_______|

       __   __    __  .___  ___. .______    __    __    ______        _______.___________.
      |  | |  |  |  | |   \/   | |   _  \  |  |  |  |  /  __  \      /       |           |
      |  | |  |  |  | |  \  /  | |  |_)  | |  |__|  | |  |  |  |    |   (----`---|  |----`
.--.  |  | |  |  |  | |  |\/|  | |   ___/  |   __   | |  |  |  |     \   \       |  |
|  `--'  | |  `--'  | |  |  |  | |  |      |  |  |  | |  `--'  | .----)   |      |  |
 \______/   \______/  |__|  |__| | _|      |__|  |__|  \______/  |_______/       |__|


gmec-ord97 12:16:56 (EDT) ~ % hostname
gdce-jumphost-7dc6885476-ff4hp
```

Once connected to the jumphost, you will have read-only access to the GDCE
cluster. This will provide you the ability to view and explore all resources
across the cluster, but not to edit or modify resources on the cluster. If you
need to edit or modify resources, continue to use Connect Gateway.

Permissions for the jumphost is facilitated through a Kubernetes `ClusterRole`
defined in [cluster-role.yaml](helm/templates/cluster-role.yaml). You can adjust the
permissions as needed through this `ClusterRole`.

### Troubleshooting
- The GDCE jumphost does not require and will not accept a password for the
`jump` user; it's all public-key authentication. If you receive a
`jump@10.223.172.245: Permission denied (publickey,keyboard-interactive).` error
message, confirm that:
  - Your public key was successfully applied to the server:
  `kubectl get configmap authorized-ssh-keys -n gdce-jumphost -o yaml`
  - Your SSH client is using the correct _private_ key to validate the public
  key offered by the jumphost. To explicitly define the private key used to
  login to the jumphost: `ssh -i <path-to-private-key> jump@10.223.172.245`
  - If all else fails, enable verbose output in your ssh client, and inspect the
  information returned: `ssh -v jump@10.223.172.245`

- If you _still_ can't log in, you are likely attempting to login as a user
other than `jump`. Most commonly this is caused by _not_ specifying the user
with your `ssh` command. Always login with `jump@<jumphost-hostname>`
(see below for some tips to improve this).

## Tips 😎
- Create an SSH config for each jumphost you use regularly.
  - An [SSH config](https://linux.die.net/man/5/ssh_config) allows you to define
  a configuration file where you can store different SSH options for each remote
  machine you connect to. This provides a quick and easy way to have an alias
  for each jumphost.

    Using the jumphost example from above, you could create an SSH config like:

    ```
    Host jump
      HostName 10.223.172.245 # You could also use a hostname instead of an IP address
      User jump
      Compression yes
      ServerAliveInterval 30
    ```

    With this SSH configuration file, you can now simply `ssh jump`. Your
    SSH client will auto-populate the needed information from your config for
    this host!
  - On macOS and Linux, these configurations are typically stored in `~/.ssh/config`.

- [tmux](https://github.com/tmux/tmux/wiki) is also installed in the jumphost.
If you would like to persist your Terminal sessions across workstation reboots,
laptop going to sleep, network dropouts, etc - check out tmux.

- Use SSH tunneling to interact with remote applications locally
  - SSH tunneling creates a secure connection between a local computer and a
  remote machine through which services can be relayed. What this means in
  practice is, you can deploy an application on a remote GDCE cluster, and
  through a combination of [Kubernetes
  port-forwarding](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/)
  and [SSH tunneling](https://help.ubuntu.com/community/SSH/OpenSSH/PortForwarding),
  view and interact with that application on your local workstation.

    Let's say you deploy an in-development web application Pod on a GDCE server,
    and wish to interact with the web application, or perhaps perform visual or
    functional testing on the deployed version of this application. With SSH
    tunneling, you can point your web browser or test suite at something like
    http://localhost:8888, which will then forward your request to the jumphost,
    which then relays the traffic to the application Pod.

  - Open a terminal window and enter the following command:
    `ssh -L 8888:localhost:8080 jump@<jumphost-hostname>`
  - This will initiate an SSH connection to `<jumphost-hostname>` along with an
  SSH tunnel. The SSH tunnel will forward all traffic from your workstation on
  TCP/8888 through the SSH tunnel to whatever service is listening on TCP/8080
  on the jumphost.

    After connecting you will notice you're just sitting at a command prompt.
    We'll now configure the second part of this tunnel, connecting the jumphost
    with your k8s Pod.

    Now, enter the following command:
    `kubectl port-forward <pod-name> <local port>:<remote port>`. For example:
    `kubectl port-forward nginx -n default 8080:80`. This will forward any
    request on the jumphost port 8080 to the `nginx` pod on port 80.

    The entire request flow looks something like:
    ```
    Local Workstation---|SSH Tunnel|--->Jumphost--->Kube port-forward---> Pod
    ```

    With this now in place, you should be able to point a web browser to
    http://localhost:8888, and see the version of your web application running
    in GDCE.

    If your GDCE Pod is hosting an API, the same concepts apply, but perhaps
    you access it with curl:

    `curl http://localhost:8888/api/inventory/id/12345`

  - You can also inline the `kubectl port-forward` _with_ your `ssh -L` command:

  `ssh -L 8888:localhost:8080 jump@<jumphost-hostname> "kubectl port-forward nginx 8080:80"`


## VM Management with the Jumphost
Creation, deletion and state management of VMs can be managed through the GCP Connect
Gateway. Access to both the graphical (VNC) and text-based serial console, SSH access and
port-forwarding (among others) is not available through GCP Connect gateway, but can be
utilized through the GDCE Jumphost.

In all cases you will need to use the jumphost as the platform which executes the Kubevirt
`virtctl` commands, and in many cases you can use SSH tunneling to emulate a native
experience (e.g. using your local applications to connect to VMs running on GDCE).


### VM Serial Console Access
Kubevirt does not provide the capability to access the serial console remotely, so this
is only available locally from the jumphost.

`kubectl virt console linux-vm -n namespace`


### VM Graphical Console (VNC)
Kubevirt provides access to the graphical console of a VM through the VNC protocol. The
graphical console is especially useful when building a Windows VM directly in GDCE, or
for displaying the GUI of other VMs which don't provide other remote viewing capabilities
(e.g. RDP).

You can use SSH tunneling, combined with the virtctl `--proxy-only` argument to create
an SSH tunnel through the jumphost and into the graphical console of your VM.

In the example below, TCP port 5900 is used to establish a VNC connection to the VM's
graphical console:

`ssh -L 5900:localhost:5900 jump "kubectl virt vnc --proxy-only --port 5900 vm-name-here -n namespace"`

Once the tunnel has been established, you can then use a local VNC client to view the
graphical console of your VM. You will configure your VNC client to connect to
`localhost:5900`, which will then pass the traffic through the tunnel to your VM.


### VM SSH Access
If you do not have network-based SSH access to a VM running in GDCE, you can us the SSH
client provided by `virtctl` to access a shell in your VM through SSH. Again here, you
can run this command locally from the jumphost:
`kubectl virt ssh user@linux-vm` or `kubectl virt scp file.txt user@linux-vm:~/`


### VM Port-Forwarding
