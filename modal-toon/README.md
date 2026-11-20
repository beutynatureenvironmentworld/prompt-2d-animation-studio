# Modal GPU pilot — original 2D slapstick

STATE: Code staged. Not deployed on the user's Modal workspace; no new Modal GPU video has been rendered. No Modal credits have been spent by these GitHub file changes.

This is an opt-in Lightricks/LTX-Video (lightweight earlier generation) image-to-video test. It is NOT the earlier ZeroGPU LTX 2.3 or Wan 2.2, and the resulting motion quality may be different.

## Starter credit warning
Your screenshot says $1 of $30/mo in accessible free credits and asks for a payment method to unlock the remainder. Official Modal Starter includes $30/month free compute, but separately priced Model APIs are not included. Setting a Workspace budget/usage limit is important before attaching payment details.

See https://modal.com/pricing

## Test instructions (manual only)
1. In Modal account settings create an API token. Do not paste it into chat and do not commit it to GitHub.
2. For CLI on your own device: install Modal with pip install modal, then run modal token set. For GitHub Actions, the separate Actions secrets would be MODAL_TOKEN_ID and MODAL_TOKEN_SECRET. The empty Modal Secrets tab in the screenshot is for runtime application credentials, not for authenticating GitHub to Modal.
3. Make an ORIGINAL character starting image PNG with the singer, headphones, cable, plug, and prankster clearly drawn. Retain the identical art for every subsequent clip.
4. Choose whether you want to spend some of the accessible $1 on a single GPU test. Cold startup, checkpoint download and loaded-container time may be billable. The software is not free beyond account allowances.
5. From the checked-out repository with access to Modal authentication, execute ONE invocation:

modal run modal-toon/pilot.py --image-path ./your_cartoon.png --prompt "Two original hand-drawn 2D cartoon women in a colorful room. The singer with pink headphones joyfully dances. The second girl bends, reaches to the audio player, physically grips and pulls out the headphone cable plug. The singer jolts in surprise. Fluid expressive arm and body movement, natural weight shifting, anticipation, quick shocked facial reaction, cohesive exact characters and room, no changing clothing, no mechanical puppet poses, no 3D, no text." --output headphone_modal_test.mp4

6. Check the MP4 for identity drift, unnatural limbs, missing audio plug, over-slow motion, and good anticipation. Render next shots only if this passes.

## Story motion recipe
First shot 2s: singer's genuine dancing, head bounce, expressive hands.
Second shot 2s: prankster's feet plant, bends to player, visibly grasps and pulls jack.
Third shot 2s: performer freezes for a beat, jaw drops, sudden comic yell.
Fourth shot 2s: reveal/laughter and fast reaction close-up.

Make separated GPU clips for natural motion, then control comedic cuts and precise audio with FFmpeg. If hand/cable contact is warped, fix those exact frames with original drawn keyframes. Original characters and a fresh joke rather than copying a reference character design.

## Security and cost controls
- No auto-deploy and no public endpoint.
- GPU profile in pilot.py: L40S, one container maximum, scaledown_window=0. L40S GPU rate currently $0.000542/second plus CPU/memory and other applicable costs. Duration of the generated movie is NOT GPU runtime.
- First prove the model works before deploying an authenticated REST endpoint. The sample endpoint in your prompt returns a placeholder success/video_url but does NOT actually produce video.
- A future Modal @modal.fastapi_endpoint should have requires_proxy_auth=True. Endpoint proxy tokens (wk-/ws-) differ from SDK API tokens (ak-/as-). Use only secret storage, not copy-pasted chat messages.
- This lightweight pilot is not a guarantee of the LTX 2.3/ Wan 2.2 quality you liked from ZeroGPU.

Official links:
https://modal.com/docs/guide/useful-snippets
https://modal.com/docs/sdk/py/latest/fastapi_endpoint
https://modal.com/docs/cli/latest/workspace
https://huggingface.co/docs/diffusers/api/pipelines/ltx_video
