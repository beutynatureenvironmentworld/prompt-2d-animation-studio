import {makeProject} from '@revideo/core';
import scene from './scene.js';
export default makeProject({name:'Original Toilet Dash',scenes:[scene],settings:{
  shared:{background:'#f8f7f3',range:[0,Infinity],size:{x:640,y:360}},
  preview:{fps:24,resolutionScale:1},
  rendering:{exporter:{name:'@revideo/core/wasm'},fps:24,resolutionScale:1,colorSpace:'srgb'}
}});
