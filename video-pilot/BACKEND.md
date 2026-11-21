# ai.vid.best pilot backend

The public origin can serve the studio UI independently while checkout is closed. Run the API and the worker on one persistent Linux host, with the same local data directory, clock, environment and deployment. SQLite transactions reserve single-worker capacity and the trial budget for ten minutes during checkout. Pending reservations count toward the queue. A successful signed payment received too late opens a refund review. A payment callback can be replayed without starting a second render.

Install ffmpeg (including ffprobe), Python 3.11+, FastAPI, uvicorn, pydantic 2 and the Modal SDK. Run the following as a dedicated unprivileged service account. Configure the process supervisor to restart both services, killing the worker's whole process group on stop. Preserve the database and output directory across deployments. Use a dedicated data directory outside the web root, readable only by the service account. Disable HTTP access logs containing private order links at both the proxy and origin.

    uvicorn backend:app --host 127.0.0.1 --port 8042 --no-access-log
    python backend.py worker

Reverse proxy /api/* to port 8042. Keep the API bound to loopback when using a local reverse proxy. Apply an edge rate limit to checkout, plus a maximum incoming request body size (16 KiB is enough). Exclude /api/* from CDN caching. Rate limiting should preserve access for PayHere's callback. Configure BASE_URL to the public HTTPS origin. Configure Modal authentication for the worker only, using Modal secrets or environment variables.

## Required settings

| Name | Meaning |
| --- | --- |
| VIDEO_DATA | Persistent directory on one host; never a static file directory |
| PAYHERE_MERCHANT_ID, PAYHERE_MERCHANT_SECRET | Website-specific sandbox or approved live merchant credentials |
| PAYHERE_LIVE | 0 for sandbox, 1 for live |
| SMTP_HOST, SMTP_FROM, SMTP_PORT | STARTTLS mail relay, verified sender, port (defaults to 587) |
| SMTP_USER, SMTP_PASSWORD | Relay credentials when authentication is required |
| MODAL_APP, MODAL_FUNCTION | Deployed Modal app and function accepting (prompt, ratio, seconds, seed) and returning MP4 bytes |
| SHOT_GPU_SECONDS | Conservative measured GPU seconds per five-second shot including cold start overhead |
| GPU_LKR_PER_MIN | Fully loaded estimated LKR per GPU minute including desired earnings |
| ORDER_OVERHEAD_LKR | Encoding, storage, delivery and minimum earnings per order (default 30) |
| GATEWAY_FRACTION | Fraction deducted from the selling price by the gateway (default estimate 0.04); set from merchant contract |
| ORDER_BUFFER_SECONDS | Extra measured wall time per order for startup, encoding and delivery (default 240) |
| BENCHMARK_MAX_SECONDS | Longest verified production duration, up to 1800. Verify each offered aspect ratio |
| FREE_GPU_SECONDS, BUDGET_START_UNIX | Conservative remaining GPU seconds allocated to this pilot and the beginning of the accounting period (Unix timestamp). Reserve funds for other workloads sharing the account |
| CHECKOUT_ENABLED | Set to 1 after a sandbox purchase, benchmark, actual mail delivery and free-credit spend cap verification |

The quote is ceil((ceil(duration / 5) × SHOT_GPU_SECONDS × GPU_LKR_PER_MIN / 60 + ORDER_OVERHEAD_LKR) / (1 − GATEWAY_FRACTION)). Preview numbers use estimates and are not a claim of measured GPU performance. An order is admitted only if queued estimates, payment reservation window and render time fit within the three-hour window. The model generates successive shots independently from the brief. Test long-form narrative consistency separately. The parent worker stops late jobs, marks the order for refund review and withholds its download. Model-side runtime limits and the provider-enforced credit cap are also required. A full paid order reserves its entire estimated GPU time even if refunded; an operator should reconcile actual bills before refreshing the budget.

## Merchant pilot

Start with PAYHERE_LIVE=0. Configure the approved website and a publicly reachable /api/payhere callback. Payment receipt relies on the signed merchant, order, amount, currency and payment status plus the amount recorded when checkout started. The browser return page cannot mark an order as paid. Customers supply Visa details at PayHere. Register the settlement bank account through the merchant dashboard. Keep banking and merchant credentials out of the repository.

Send a sandbox payment, close the browser, confirm one queued order, verify an actual MP4 of the requested duration and ratio, then verify that the email opens its private status page. Benchmark a representative queue under your own Modal spend limit. Free credits and compute availability can fluctuate. Choose conservative estimates, shorten the admitted duration when appropriate, and keep production checkout closed if these tests have not passed.

Operators must monitor orders with state refund_review, resolve payments in the merchant dashboard and contact affected customers. Chargebacks revoke download access. SMTP failures are retried in five minutes. Keep sufficient local disk space, back up SQLite and remove expired outputs and customer data under your published retention policy. Download URLs are bearer secrets. The implementation does not automatically issue refunds, purge data or provide an order administration UI.
