# GDCE Jump Host

The GDCE Jump Host (jumphost) is a lightweight container-based SSH bastion host
used to interact with a local cluster's kube-apiserver, primarily through `kubectl`.
This jumphost was designed to use GDCE multinetworks, and is accessible through
a GDCE secondary (VLAN) network.

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
- `kubectl virt ssh` (Kubevirt)
- `kubectl virt console` (Kubevirt)
- `kubectl virt vnc` (Kubevirt)


## Usage
The GDCE Jump Host will be installed on each GDCE cluster, and consists of a
single Pod running [OpenSSH](https://www.openssh.com/). SSH login access is
provided **only** through public-key authentication; no password-based
authentication is provided or supported.

A Kubernetes ConfigMap containing each user's SSH public key is mounted into the
Pod, and is used to authenticate a user's SSH session.

### Initial Setup
1. Generate an SSH keypair
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

If you do not have a standardized hostname or IP address scheme for various
cluster-specific jumphosts, some initial work is needed to determine the IP
address for the jumphost you're looking to connect to.

Using Connect Gateway, run the following command on the cluster hosting the
jumphost you wish to connect to:

`kubectl get pods -n gdce-jumphost -o=jsonpath='{range .items[0]}{.metadata.annotations.networking\.gke\.io/pod-ips}{end}'`

The output from this command will produce detail on the customer-assigned IP
address for this Pod:

```
[{"networkName":"store-vlan-2100","ip":"10.159.172.101"}]
```

You can now SSH into the jumphost using this IP address:

```
❯ ssh jump@10.159.172.101

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


gmec-cvg9 12:16:56 (EDT) ~ % hostname
gdce-jumphost-7dc6885476-ff4hp
```

Once connected to the jumphost, you will have read-only access to the GDCE
cluster. This will provide you the ability to view and explore all resources
across the cluster, but not to edit or modify resources on the cluster. If you
need to edit or modify resources, continue to use Connect Gateway.

### Troubleshooting
- The GDCE jumphost does not require and will not accept a password for the
`jump` user; it's all public-key authentication. If you receive a
`jump@127.0.0.1: Permission denied (publickey,keyboard-interactive).` error
message, confirm that:
  - Your public key was successfully applied to the server:
  `kubectl get configmap authorized-ssh-keys -n gdce-jumphost -o yaml`
  - Your SSH client is using the correct _private_ key to validate the public
  key offered by the jumphost. To explicitly define the private key used to
  login to the jumphost: `ssh -i <path-to-private-key> jump@10.159.172.101`
  - If all else fails, enable verbose output in your ssh client, and inspect the
  information returned: `ssh -v jump@10.159.172.101`

- If you receive a password prompt, you are likely attempting to login as a user
other than `jump`. Most commonly this is caused by _not_ specifying the user
with your `ssh` command. Always login with `jump@<jumphost-hostname>`
(see below for some tips to improve this).

### Tips 😎
- Create an SSH config for each jumphost you use regularly.
  - An [SSH config](https://linux.die.net/man/5/ssh_config) allows you to define
  a configuration file where you can store different SSH options for each remote
  machine you connect to. This provides a quick and easy way to have an alias
  for each jumphost.

    Using the jumphost example from above, you could create an SSH config like:

    ```
    Host jumplab
      HostName 10.159.172.101  # You could also use a hostname instead of an IP address
      User jump
      Compression yes
    ```

    With this SSH configuration file, you can now simply `$ ssh jumplab`. Your
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

    If your GDCE Pod is hosting an API , the same concepts apply, but perhaps
    you access it with curl:

    `curl http://localhost:8888/api/inventory/id/12345`

  - You can also inline the `kubectl port-forward` _with_ your `ssh -L` command:

  `ssh -L 8888:localhost:8080 jump@<jumphost-hostname> "kubectl port-forward nginx 8080:80"`
