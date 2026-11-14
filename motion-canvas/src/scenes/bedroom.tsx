import {Circle, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';

// This is a distinct, hand-authored *editor* scene.
// The Python CLI renderer in the repo does not generate this TypeScript.
// Keep user-supplied character references local; do not auto-upload.
export default makeScene2D(function* (view) {
  view.fill('#2b3153');
  const awakeHead = createRef<Circle>();
  const sleepingHead = createRef<Circle>();
  const floatingZ = createRef<Txt>();
  const blanket = createRef<Rect>();

  view.add(
    <>
      <Circle width={1130} height={710} fill="#48517d" position={[0, 20]}/>
      <Rect width={1280} height={200} fill="#353757" position={[0, 270]}/>
      <Rect width={210} height={315} x={468} y={-145} fill="#1b223c" stroke="#11152a" lineWidth={8}/>
      <Circle width={110} height={110} x={525} y={-200} fill="#ddeafa"/>
      <Rect width={12} height={300} x={465} y={-145} fill="#191e38"/>
      <Rect width={210} height={11} x={468} y={-145} fill="#191e38"/>
      <Rect width={440} height={360} x={-355} y={165} fill="#69668b" stroke="#15142c" lineWidth={8}/>
      <Rect width={440} height={360} x={310} y={165} fill="#6d698d" stroke="#15142c" lineWidth={8}/>
      <Rect width={400} height={100} x={-355} y={150} fill="#b6bedc" stroke="#15142c" lineWidth={6}/>
      <Rect width={400} height={100} x={310} y={150} fill="#b6bedc" stroke="#15142c" lineWidth={6}/>
      <Circle ref={awakeHead} width={120} height={120} x={-365} y={-3} fill="#e4e9f4" stroke="#15142c" lineWidth={8}/>
      <Circle ref={sleepingHead} width={120} height={120} x={295} y={-3} fill="#e4e9f4" stroke="#15142c" lineWidth={8}/>
      <Txt x={-365} y={8} fontSize={34} text=">_<" fill="#19182c"/>
      <Txt x={295} y={8} fontSize={40} text="o" fill="#161624"/>
      <Rect ref={blanket} width={520} height={190} x={310} y={235} fill="#8795c4" stroke="#15142c" lineWidth={6}/>
      <Rect width={520} height={190} x={-355} y={235} fill="#8391bf" stroke="#15142c" lineWidth={6}/>
      <Txt ref={floatingZ} x={480} y={-70} fontSize={92} text="Z z z" fill="#10172b" opacity={1}/>
    </>,
  );
  yield* all(
    floatingZ().position.y(-250, 2.2),
    floatingZ().opacity(0, 2.2),
    sleepingHead().position.y(4, 1.1).to(-3, 1.1),
    awakeHead().rotation(4, .6).to(-3, .6).to(0, 1),
    blanket().height(196, 1.1).to(188, 1.1),
  );
  yield* waitFor(.5);
});
