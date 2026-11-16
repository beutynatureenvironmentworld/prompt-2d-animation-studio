// Native Revideo scene: actual @revideo/2d node graph, NO React JSX runtime.
import {Circle, Rect, Txt, makeScene2D} from '@revideo/2d';
import {all, waitFor} from '@revideo/core';
export default makeScene2D('original-toilet-dash', function*(view) {
  view.fill('#f8f7f3');
  const ground=new Rect({x:0,y:153,width:640,height:55,fill:'#e7e5dc'});
  const door=new Rect({x:220,y:-10,width:124,height:210,fill:'#f7f5ef',stroke:'#111',lineWidth:6});
  const smallPanel=new Rect({x:0,y:0,width:92,height:151,fill:'#fff',stroke:'#111',lineWidth:2});
  const doorknob=new Circle({x:42,y:24,size:12,fill:'#111'});
  door.add([smallPanel,doorknob]);
  const sign=new Rect({x:220,y:-132,width:116,height:31,fill:'#111'});
  sign.add(new Txt({text:'TOILET',fontSize:18,fill:'#fff'}));
  const person=new Rect({x:-170,y:55,width:60,height:77,fill:'#fff',stroke:'#111',lineWidth:5});
  // Unique independently drawn head/eyes/mouth; no imported pose image.
  const head=new Circle({x:0,y:-72,size:84,fill:'#fff',stroke:'#111',lineWidth:5});
  const eye1=new Circle({x:-17,y:-3,size:12,fill:'#111'});
  const eye2=new Circle({x:17,y:-3,size:12,fill:'#111'});
  const mouth=new Rect({x:0,y:22,width:26,height:5,fill:'#111'});
  head.add([eye1,eye2,mouth]);
  const leftArm=new Rect({x:-41,y:13,width:14,height:66,rotation:-20,fill:'#161616'});
  const rightArm=new Rect({x:41,y:13,width:14,height:66,rotation:20,fill:'#161616'});
  const leftLeg=new Rect({x:-17,y:72,width:14,height:70,rotation:15,fill:'#161616'});
  const rightLeg=new Rect({x:17,y:72,width:14,height:70,rotation:-15,fill:'#161616'});
  person.add([leftLeg,rightLeg,leftArm,head,rightArm]);
  view.add([ground,door,sign,person]);
  yield* waitFor(.62);
  // Actual animated node transforms, not a static pose zoom.
  yield* all(person.x(36,1.6),person.rotation(10,1.6),leftArm.rotation(55,1.6),
             rightArm.rotation(-45,1.6),leftLeg.rotation(-38,1.6),rightLeg.rotation(38,1.6));
  yield* all(rightArm.rotation(-115,.45),person.rotation(0,.45)); // knock
  yield* all(mouth.height(22,.38),head.scale(1.11,.38),door.rotation(4,.38)); // shock
  yield* all(person.x(-25,.52),person.rotation(-14,.52),leftArm.rotation(-80,.52));
  yield* all(person.rotation(0,.43),head.scale(1,.43),mouth.height(5,.43),leftLeg.rotation(4,.43));
  yield* waitFor(.6);
});
