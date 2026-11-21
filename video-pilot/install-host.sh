#!/usr/bin/env bash
set -euo pipefail
# Run as root on the persistent API host after installing ffmpeg and the venv.
cd "$(dirname "$0")"
base=/opt/vidbest-video-pilot
getent passwd vidbest-pilot >/dev/null || useradd --system --home /var/lib/vidbest-video-pilot --shell /usr/sbin/nologin vidbest-pilot
install -d -m755 "$base/app" /etc/vidbest-video-pilot
install -m644 backend.py web.py policy.html index.html "$base/app/"
for job in api worker; do
  if [[ $job == api ]]; then
    cmd="$base/venv/bin/uvicorn web:app --host 127.0.0.1 --port 8193 --no-access-log --no-proxy-headers"
  else
    cmd="$base/venv/bin/python backend.py worker"
  fi
  cat >"/etc/systemd/system/vidbest-video-$job.service" <<UNIT
[Unit]
Description=vid.best video pilot $job
After=network-online.target
[Service]
User=vidbest-pilot
WorkingDirectory=$base/app
StateDirectory=vidbest-video-pilot
StateDirectoryMode=0700
Environment=VIDEO_DATA=/var/lib/vidbest-video-pilot
EnvironmentFile=-/etc/vidbest-video-pilot/common.env
EnvironmentFile=-/etc/vidbest-video-pilot/$job.env
ExecStart=$cmd
Restart=always
RestartSec=5
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
UMask=0077
[Install]
WantedBy=multi-user.target
UNIT
done
sed -e 's/^Description=.*/Description=Archive a private video support copy/' \
    -e 's/backend.py worker$/backend.py archive/' -e '/^Restart/d' \
    -e '/^\[Service\]/a Type=oneshot' /etc/systemd/system/vidbest-video-worker.service > /etc/systemd/system/vidbest-video-archive.service
cat >/etc/systemd/system/vidbest-video-archive.timer <<UNIT
[Timer]
OnBootSec=2min
OnUnitInactiveSec=2min
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now vidbest-video-archive.timer
systemctl enable --now vidbest-video-api.service vidbest-video-worker.service
systemctl restart vidbest-video-api.service vidbest-video-worker.service

