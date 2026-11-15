# Hugging Face storage readiness

Read-only check for user-provided encrypted GitHub Actions secret \`HF_TOKEN\`. Calls the official HF \`whoami-v2\` API, and checks whether the private dataset \`<authenticated-user>/vidbest-animation-storage\` already exists. Does not log token, username, private URLs or account IDs. Does not create repositories, upload model weights or use GPU quota.

This remains optional. Public model files can be downloaded from the HF Hub without requiring a personal token for many models. Full access token is unnecessarily broad: a scoped write token for a specific private dataset would be safer. Once a repository ID and write rights are explicitly verified, a separate reviewed, manual-only workflow can upload licensed source assets/weights. Check Hugging Face's per-account private storage, quotas and redistribution restrictions before any large upload.
