# Config Sync Setup

1. Create and save a Github
[Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

2. Create a new Secret on the cluster:
```
kubectl create ns config-management-system
```
```
kubectl create secret generic git-creds \
  --namespace="config-management-system" \
  --from-literal=username=gdce-homelab \
  --from-literal=token=<token-here>
```
Note: the `username` field does not matter when using a PAT. It's simply used for display
within the CLI and UI.

3. Ensure Config Sync is enabled in the cluster:
`gcloud beta container fleet config-management enable`

4. Apply the Config Sync configuration to the cluster
```
gcloud beta container fleet config-management apply \
    --membership=gdce-homelab \
    --config=config-sync-config.yaml \
    --project=living-on-the-edge
```

5. Verify the installation
```
gcloud beta container fleet config-management status \
    --project=living-on-the-edge
```

For full detail, review the
[Config Sync installation documentation](https://cloud.google.com/kubernetes-engine/enterprise/config-sync/docs/how-to/installing-config-sync).
