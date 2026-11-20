#!/usr/bin/env bash
# Clone official Applio/RVC; full installation only with --full.
set -euo pipefail
MODE="--source-only"; DIR="third_party/Applio"
if [ "$#" -ge 1 ]; then MODE="$1"; fi
if [ "$#" -ge 2 ]; then DIR="$2"; fi
case "$MODE" in --source-only|--full) ;; *)
  echo "Usage: $0 --source-only|--full [install_dir]"; exit 2 ;;
esac
command -v git >/dev/null || { echo 'Git required'; exit 2; }
if [ ! -f "$DIR/run-install.sh" ]; then
  mkdir -p "$(dirname "$DIR")"
  git clone --depth 1 https://github.com/IAHispano/Applio.git "$DIR"
fi
test -f "$DIR/run-install.sh" && test -f "$DIR/run-applio.sh"
echo "APPLIO_SOURCE_READY $DIR"
echo "Use only voice models and recordings you have rights to use."
if [ "$MODE" = "--full" ]; then
  cd "$DIR"
  bash ./run-install.sh
  echo "APPLIO_INSTALL_SCRIPT_COMPLETED"
else
  echo "APPLIO_NOT_INSTALLED: official source verified; --full installs engine deps."
fi
