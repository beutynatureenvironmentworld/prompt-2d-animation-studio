#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
for package in blender krita inkscape synfigstudio opentoonz tahoma2d pencil2d ffmpeg; do
  if apt-cache show "$package" >/dev/null 2>&1; then
    echo "Installing optional package: $package"
    sudo apt-get install -y --no-install-recommends "$package" || echo "Package could not be installed: $package"
  else
    echo "Not in this Ubuntu apt configuration: $package"
  fi
done
for tool in blender krita inkscape synfig opentoonz ffmpeg; do
  command -v "$tool" || true
done
echo "GitHub hosted runner is temporary; nothing is installed permanently."
