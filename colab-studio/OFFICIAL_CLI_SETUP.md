# Official Google Colab CLI — GitHub Actions integration (November 2026)

## Sinhala

Google 2026 ජූනි 5 හඳුන්වා දුන් official Google Colab CLI භාවිත කරයි. Kaggle වගේ API key එකක් නොවේ: Google OAuth 2.0 / Application Default Credentials (ADC) අවශ්‍යයි.

First run: [Official Colab CLI workflow](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/workflows/official-colab-cli.yml), choose mode **validate**. This checks installation of pinned google-colab-cli 0.7.2, no auth and NO GPU usage.

To connect a Google account from ephemeral GitHub runners, the manual check_connection and gpu_probe modes require a **GitHub encrypted repository secret** named **COLAB_ADC_JSON**. It contains Google's complete *user ADC JSON* (authorized_user, including a refresh token), created after the account owner grants authorization in a trusted local environment. **This is very sensitive and grants broad Google Cloud scopes; it is NOT a Colab-only key.** Use only a repository you fully trust and ideally a separate Google account with no unrelated cloud resources. Revoke it immediately if leaked. Never send the credentials, access token, OAuth authorization code or password in ChatGPT, Git commits or screenshots.

Official instructions for login from trusted machine with Google Cloud SDK:

```bash
gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/colaboratory
```

The resulting private ADC JSON is typically located at ~/.config/gcloud/application_default_credentials.json. Only if you consciously accept its broad scope, save its entire contents to https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/settings/secrets/actions under name COLAB_ADC_JSON.

**Do not do this if you cannot protect your Google account token.** As a safer alternative, use your already existing interactive Colab notebook and do not add COLAB_ADC_JSON.

After authorizing, run the GitHub workflow manually with **check_connection**. It only verifies the connection; no GPU is requested. Then optionally select **gpu_probe** which tries ONE T4 GPU, performs a tiny CUDA operation, saves JSON evidence, and stops the runtime. No diffusion weights, video or paid Google Cloud GPU are used by the workflow. GPU access/free quota is NOT guaranteed.

No GitHub push launches a GPU. No SSH, proxy tunnels, remote UI, unattended workers, artificial keepalive or quotas bypass. Actual 2D image-to-video would need separately verified GPU inference code and model licenses.

## English

Official Apache-2.0 Google CLI source: https://github.com/googlecolab/google-colab-cli
Authentication: https://github.com/googlecolab/google-colab-cli/blob/main/docs/04_automation_and_utility.md
Colab terms and free limits: https://research.google.com/colaboratory/faq.html

Mode validate checks installation, shell commands and Python syntax in GitHub Actions. Mode check_connection reads explicitly configured ADC credentials from a temporary permission-0600 file without printing values. Mode gpu_probe requests one T4 GPU and stops it on exit; a failure or 400/403 means that free GPU access is not currently available/authorized. This is not a promise of free GPU hours, constant runtime, persistent sessions or successful AI video rendering.

Google Colab Enterprise is a distinct potentially billable Google Cloud product; this workflow does not activate it.
