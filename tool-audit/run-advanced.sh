#!/usr/bin/env bash
set -Eeuo pipefail
TOOL="$1"; OUT="tool-audit/results/$TOOL"; mkdir -p "$OUT"
echo "TOOL=$TOOL" > "$OUT/report.txt"
trap 'rc=$?; echo "EXIT=$rc" >> "$OUT/report.txt"; echo "RESULT=$([ "$rc" -eq 0 ] && echo PASS || echo FAIL)" >> "$OUT/report.txt"' EXIT
case "$TOOL" in
opencode)
  mkdir -p "$OUT/node"; cd "$OUT/node"
  npm init -y
  npm install --no-audit --no-fund @opencode/cli
  npx opencode --version
  echo 'SCOPE=OpenCode CLI binary/version; no LLM model or code generation' >> ../report.txt;;
remotion)
  mkdir -p "$OUT/node"; cd "$OUT/node"
  npm init -y
  npm install --no-audit --no-fund remotion @remotion/cli react react-dom
  cat > index.js <<'JS'
import React from "react";
import {registerRoot,Composition} from "remotion";
const Color=()=>React.createElement("div",{style:{width:"100%",height:"100%",background:"#94bcff"}});
registerRoot(()=>React.createElement(Composition,{id:"Color",component:Color,durationInFrames:12,fps:12,width:160,height:90}));
JS
  npx remotion still index.js Color ../remotion.png --log=error
  test -s ../remotion.png
  echo 'SCOPE=real Chromium-rendered Remotion still (NOT video)' >> ../report.txt;;
revideo)
  mkdir -p "$OUT/node"; cd "$OUT/node"
  npm init -y
  npm install --no-audit --no-fund @revideo/core @revideo/2d
  node -e 'import("@revideo/core").then(x=>{if(!x.makeProject)throw Error("Missing makeProject");console.log("Revideo core import PASS")})'
  echo 'SCOPE=Revideo packages installed and core import test; MP4 renderer not executed' >> ../report.txt;;
motion-canvas)
  mkdir -p "$OUT/node"; cd "$OUT/node"
  npm init -y
  npm install --no-audit --no-fund @motion-canvas/core@3.17.2 @motion-canvas/2d@3.17.2
  node -e 'import("@motion-canvas/core").then(x=>{if(!x.makeProject)throw Error("Missing makeProject");console.log("Motion Canvas core import PASS")})'
  echo 'SCOPE=Motion Canvas core and 2D installed/imported; prior PR editor build tested separately' >> ../report.txt;;
stykanimate)
  git clone --depth 1 https://github.com/filippocalippo/StykAnimate-App.git "$OUT/source"
  cd "$OUT/source"
  test -f package.json
  node --check src/app.mjs
  npm ci --ignore-scripts --no-audit --no-fund
  echo 'SCOPE=StykAnimate GPL source, syntax, npm dependencies; GUI/WebGPU export NOT tested' >> ../report.txt;;
stick)
  git clone --depth 1 https://github.com/blixvip/stick.git "$OUT/source"
  cd "$OUT/source"
  test -f package.json
  node --check src/app.mjs
  npm ci --ignore-scripts --no-audit --no-fund
  echo 'SCOPE=Stick GPL source, syntax, npm dependencies; GUI/WebGPU export NOT tested' >> ../report.txt;;
krita)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends krita
  dpkg-query -W krita
  echo 'SCOPE=GUI software installed (no automated drawing/export)' >> "$OUT/report.txt";;
pencil2d)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends pencil2d
  dpkg-query -W pencil2d
  echo 'SCOPE=GUI software installed (no automatic animation render)' >> "$OUT/report.txt";;
opentoonz)
  sudo apt-get update -qq
  if apt-cache show opentoonz >/dev/null 2>&1; then
    sudo apt-get install -y --no-install-recommends opentoonz
    dpkg-query -W opentoonz
    echo 'SCOPE=system package installation; GUI render NOT tested' >> "$OUT/report.txt"
  else
    echo 'DETAIL=NOT_INSTALLED: no OpenToonz package in stock Ubuntu 24.04 apt repositories' >> "$OUT/report.txt"
  fi;;
moneyprinterturbo)
  git clone --depth 1 https://github.com/harry0703/MoneyPrinterTurbo.git "$OUT/source"
  test -f "$OUT/source/README-en.md"
  echo 'SCOPE=SOURCE_CHECKOUT_ONLY; not a functioning install/AI video service' >> "$OUT/report.txt";;
*) echo "Unknown tool $TOOL" >&2; exit 2;;
esac
echo "Smoke finished: $TOOL"
