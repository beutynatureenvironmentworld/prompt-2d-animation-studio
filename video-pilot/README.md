# ai.vid.best video pilot

A Cloudflare Tunnel serves the studio and quote API from the existing Oracle host. Checkout defaults to closed. The public can explore the editor and indicative LKR prices. No prompt or customer information is submitted when configuring a closed quote.

The Modal staging workflow is manual. GitHub reads the existing repository or video-pilot environment secrets MODAL_TOKEN_ID and MODAL_TOKEN_SECRET. Accept the official gated Hugging Face model and set HF_TOKEN in the private Modal secret vidbest-huggingface. The workflow stages weights and deploys the private inference function. See [engine setup](ENGINE.md).

The Oracle API and worker use separate systemd services. install-host.sh installs the UI and API into /opt/vidbest-video-pilot/app using a prepared venv at /opt/vidbest-video-pilot/venv. Store shared pricing and pilot configuration in /etc/vidbest-video-pilot/common.env. Keep PayHere credentials in api.env and SMTP and Modal credentials in worker.env, all root-owned with mode 0600. The API needs availability flags for SMTP_HOST and SMTP_FROM in common.env. Run a sandbox purchase, confirm email delivery, check the actual account spending limit and benchmark the longest admitted order before switching to live checkout. See [checkout and rendering](BACKEND.md) for settings and the refund-review process.

The public estimate is provisional. The default profile allows a hypothetical 45 GPU seconds per 5-second clip. A 30-minute video requires 360 clips. Three hours would allow at most 30 wall-clock seconds per clip before encoding, queue and delivery overhead. The pilot rejects that duration under the default profile. Grant access to longer jobs only when supported by an end-to-end benchmark.
