import {renderVideo} from '@revideo/renderer';
import {mkdirSync} from 'node:fs';
async function run(){
  mkdirSync('out',{recursive:true});
  const output=await renderVideo({
    projectFile:'./src/project.ts',
    settings:{outDir:'out',outFile:'toon-revideo.mp4',workers:1,
      logProgress:true,ffmpeg:{ffmpegPath:'ffmpeg',ffmpegLogLevel:'error'},
      puppeteer:{args:['--no-sandbox']}}
  });
  console.log('ORIGINAL_REVIDEO_REAL_MP4_COMPLETE',output);
}
run().catch(e=>{console.error('REVIDEO_NATIVE_RENDER_FAILED',e.message);process.exit(1)});
