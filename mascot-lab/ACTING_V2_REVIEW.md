# Funny Toon Ever — Facial Acting V2 and Contact QA

## Implemented
- Uses exact original permanent six-pose source (mascot-lab/config/permanent_mascot.webp), not newly regenerated identity.
- OpenCV detects source circular head per pose. Internal face is rebuilt with exactly one visible pupil in each eye, and 6 expressions (focus, effort, shock, worried, neutral, grin).
- Changes face only, original authored silhouette and hand/leg pose artwork remains unchanged.
- Knock stages now use the original right-fist source pose, solve its image anchor to the authored door point x245/y375, and recoil between three contacts.
- Two contact-recoil candidates are rendered, and QA decodes the actual MP4 to compare fist impact vs withdrawal.
- Works on CPU with Pillow, OpenCV and FFmpeg, without paid APIs or GPU.

## Limitations and truthful claims
- This is NOT independent elbow/shoulder or knee/heel IK: whole-pose source cutouts still control limbs. Fist anchoring is calibrated and visible, but collision and articulated motion can be improved further.
- The original grin is deliberately not fixed on every frame; faces are authored overlays, not a learned video diffusion model.
- Explicit pupil count is validated in generated overlays, but actual footage still needs a human visual review for stray black contours or style drift.
- The door is fixed authored geometry; arbitrary objects and environments require adding scene graph anchors and poses.
- The QA scoring reads frames, pixels and approximate geometry; it is not autonomous human-level video understanding.

## Run
Go to the Actions workflow Funny Toon Ever Mascot V2 — Facial and Hand Contact Proof.
All changes remain separate from main, on experiment/mascot-face-and-contact-v2 until reviewed. The existing hourly automation watches experiment/hourly-mascot-qa-loop; merge into that experimental branch after QA succeeds.

Next priority: a reusable source-head puppet with genuinely articulated arms and planted foot IK, plus per-object contact anchors. Independent skeleton rigging is not claimed complete.