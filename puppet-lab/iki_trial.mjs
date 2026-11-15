/**
 * New isolated Iki experiment: actually auto-rig PNG layers with Iki's API,
 * validate the open .iki file and render 3 DIFFERENT facial parameter poses.
 * Input art is the official Iki MIT-licensed fixture recolored by our code,
 * not newly AI-drawn character art. The motion storyboard is prompt-compiled.
 */
import fs from "node:fs";
import path from "node:path";
import { autoRigFromLayers, validateIki, describeIki, renderPoses } from "../packages/mcp/dist/index.mjs";

const root=process.cwd();
const fixtures=path.resolve(root,"examples/editor/fixtures/sample-layers");
const output=path.resolve(root,"puppet-test-output");
fs.mkdirSync(output,{recursive:true});
const sourceLayers=fs.readdirSync(fixtures).filter(f=>f.endsWith(".png")).map(f=>({path:path.join(fixtures,f)}));
if(sourceLayers.length<4)throw new Error("Official Iki fixture PNG layers not found");
const rig=await autoRigFromLayers({
  layers:sourceLayers,
  outputPath:path.join(output,"funny-boy-auto-rig.iki")
});
if(!rig.ok)throw new Error("Iki auto-rig failed: "+rig.error);
const file=JSON.parse(fs.readFileSync(rig.path,"utf8"));
file.name="VidBest original ink-animation puppet experiment";
fs.writeFileSync(rig.path,JSON.stringify(file));
const val=validateIki(file);
if(!val.ok)throw new Error("Invalid auto-generated Iki rig: "+val.error);
const detail=describeIki(file);
if(!detail.ok)throw new Error("Could not describe Iki: "+detail.error);
const params=file.parameters.map(x=>x.id);
const mouth=params.find(x=>x.includes("MouthOpen"));
const eye=params.filter(x=>/^ParamEye[LR]Open$/.test(x));
const blink=Object.fromEntries(eye.map(e=>[e,0]));
const smile=mouth?{[mouth]:1}:{};
const poses=[{name:"01-idle",values:{}},
 {name:"02-mouth-open",values:smile},
 {name:"03-eye-blink",values:blink}];
for (let i=0;i<24;i++){
  const p=i/24;
  const turn=Math.round(22*Math.sin(2*Math.PI*p));
  const nod=Math.round(9*Math.sin(2*Math.PI*p+.9));
  const tilt=Math.round(7*Math.sin(2*Math.PI*p+1.9));
  const open=(i>=6 && i<=18) ? ([.1,.5,.8,.25,.9,.3][i%6]) : 0;
  const shut = i===5 || i===6 || i===17;
  const values={"ParamAngleX":turn,"ParamAngleY":nod,"ParamAngleZ":tilt,
    ...(mouth?{[mouth]:open}:{}),
    ...Object.fromEntries(eye.map(e=>[e,shut?0:1]))};
  poses.push({name:"face_"+String(i+1).padStart(3,"0"),values});
}
if(!mouth || eye.length<2)throw new Error("Auto-rig must include mouth and both eye blink controls");
const dest=path.join(output,"iki-poses");
fs.mkdirSync(dest,{recursive:true});
const renders=await renderPoses({modelPath:rig.path,outDir:dest,poses});
if(!renders.ok)throw new Error("Iki WebGL/Chromium render_poses failed: "+renders.error);
for(const pose of poses){
 const p=path.join(dest,pose.name+".png");
 if(!fs.existsSync(p)||fs.statSync(p).size<2000)throw new Error("Missing real pose render "+p);
}
const report={
 source:"Iki MIT 0.x auto-rig and WebGL2 browser renderer",
 sample_art:"Official Iki MIT fixture PNGs (NOT AI-generated)",
 from_prompt:"motion-plan compiled independently, not a true text-to-image layer generator",
 model_generated:true,valid_open_iki:true,
 original_user_art_created:false,
 face_pose_images_rendered:poses.length,
 full_body_walk_from_iki_verified:false,
 part_count:file.parts.length, parameter_count:file.parameters.length,
 blink_parameter_ids:eye, mouth_parameter_id:mouth,
 important:"This validates real Iki rig creation and three WebGL pose renders. It does not prove instant perfect full-body auto-animation."
};
fs.writeFileSync(path.join(output,"iki-report.json"),JSON.stringify(report,null,2)+"\n");
console.log("IKI_AUTO_RIG_REAL_MODEL_AND_POSE_SWEEP_PASS",JSON.stringify({parts:report.part_count,params:report.parameter_count}));
