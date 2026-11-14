#!/usr/bin/env bash
set -Eeuo pipefail
ENGINE="$1"
OUT="$PWD/render-compare/results/$ENGINE"
mkdir -p "$OUT"
echo "ENGINE=$ENGINE" > "$OUT/report.txt"
trap 'rc=$?; echo "EXIT=$rc" >> "$OUT/report.txt"; echo "STATUS=$([ "$rc" -eq 0 ] && echo MP4_RENDER_PASS || echo MP4_RENDER_FAIL)" >> "$OUT/report.txt"' EXIT
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends ffmpeg nscd
cd "$OUT"
npm init -y >/dev/null
if [ "$ENGINE" = "remotion" ]; then
  npm install --no-audit --no-fund remotion @remotion/cli react react-dom
  cat > index.js <<'JS'
import React from "react";
import {registerRoot,Composition} from "remotion";
const Color=()=>React.createElement("div",{style:{width:"100%",height:"100%",background:"#243e69"}});
registerRoot(()=>React.createElement(Composition,{id:"Color",component:Color,durationInFrames:12,fps:12,width:160,height:90}));
JS
  npx remotion render index.js Color "render.mp4" --codec=h264 --concurrency=1 --log=error
elif [ "$ENGINE" = "revideo" ]; then
  npm install --no-audit --no-fund @revideo/core @revideo/2d @revideo/renderer @revideo/ffmpeg @revideo/ui @revideo/vite-plugin vite@4.5.14 tsx typescript
  mkdir -p src/scenes
  cat > src/scenes/example.tsx <<'TSX'
import {makeScene2D, Circle} from '@revideo/2d';
import {waitFor} from '@revideo/core';
export default makeScene2D(function* (view) {
  view.add(new Circle({width:80, height:80, fill:'#fbcc53'}));
  yield* waitFor(0.65);
});
TSX
  cat > src/project.ts <<'TS'
import {makeProject} from '@revideo/core';
import scene from './scenes/example?scene';
export default makeProject({
  scenes:[scene],
  settings:{shared:{size:{x:160,y:90}},rendering:{fps:12}},
});
TS
  cat > vite.config.ts <<'TS'
import {defineConfig} from 'vite';
import pluginImport from '@revideo/vite-plugin';
const wrapped = pluginImport as unknown as {default?:typeof pluginImport};
const plugin = typeof pluginImport === 'function' ? pluginImport : wrapped.default;
if (typeof plugin !== 'function') throw new Error('Revideo Vite plugin unavailable');
export default defineConfig({plugins:[plugin()]});
TS
  cat > src/render.ts <<'TS'
import {renderVideo} from '@revideo/renderer';
async function main() {
 const file=await renderVideo({projectFile:'./src/project.ts',settings:{
  outFile:'render.mp4',outDir:'.',workers:1,range:[0,0.65],dimensions:[160,90],
  logProgress:true,ffmpeg:{ffmpegPath:'ffmpeg'},puppeteer:{args:['--no-sandbox']}
 }});
 console.log("Revideo output",file);
}
main().catch(e=>{console.error(e);process.exitCode=1});
TS
  npx tsx src/render.ts
else
  echo "Unknown renderer: $ENGINE" >&2; exit 2
fi
test -s render.mp4
ffprobe -v error -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 render.mp4 | tee video_metadata.txt
echo 'SCOPE=actual 0.65-1 second silent H264 MP4 produced by headless renderer on CPU' >> report.txt
