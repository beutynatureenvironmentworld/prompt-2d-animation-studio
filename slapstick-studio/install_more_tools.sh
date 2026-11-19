#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
work="/tmp/slapstick-animation-tools"
mkdir -p "$work/tahoma"
echo 'Downloading official Tahoma2D v1.6.3 Linux portable'
curl -fL --retry 3 --connect-timeout 25 'https://github.com/tahoma2d/tahoma2d/releases/download/v1.6.3/Tahoma2D-linux-clang.tar.gz' -o "$work/tahoma.tar.gz"
tar -xzf "$work/tahoma.tar.gz" -C "$work/tahoma"
path=$(find "$work/tahoma" -name 'Tahoma2D.AppImage' -type f -print -quit)
test -n "$path" && test -s "$path"
chmod +x "$path"
file "$path"
sha256sum "$path"
echo 'Tahoma2D portable package downloaded and checked. GUI not launched.'
echo 'Installing community OpenToonz Flatpak'
sudo apt-get update -qq
sudo apt-get install -y -qq flatpak
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
sudo flatpak install -y --noninteractive flathub io.github.OpenToonz
sudo flatpak info io.github.OpenToonz
echo 'Installation verified, no GUI/video rendering. Disposable runner.'
