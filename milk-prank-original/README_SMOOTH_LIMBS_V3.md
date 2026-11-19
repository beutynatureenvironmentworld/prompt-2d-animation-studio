# Funny Toon Ever V3 — Invisible IK, smooth original limbs

## Artistic rules from user review
- KEEP the original Snore Collector purple bedroom, expressive eyes, small white faces and overall character silhouettes.
- Arms and legs must visually read as SINGLE continuous thick black lines, as in the original source-film style.
- NEVER expose bones, rig handles, elbow circles, knee circles, wrist balls, two-segment V elbows or sharp V knees.
- Internal analytic 2-bone inverse kinematics remains allowed and is used to keep wrists and feet on real targets, but the silhouette is drawn with exactly ONE smooth quadratic Bezier stroke from shoulder-to-hand or hip-to-foot.
- At rest: limbs are essentially straight with barely perceptible curvature; during a purposeful reach/step only: very subtle curvature, capped at 7.2 SVG units of control-point offset.
- Keep foot contact world-planted; one small swing step only where the girl reaches.
- Hand/carton contact must be visible without detached hand or floating fingers; the only extra finger mark is a very small contact contour on the carton.

## Source changes and tests
- rig_ik.cjs: hidden 2-bone solver + one thick quadratic stroke per limb. Drawing has NO elbow, wrist or knee marker ellipses.
- art.cjs: removed final extra visible wrist-circle marker.
- test_smooth_limbs.cjs: tests single Bezier stroke, no visible joints, low rest curvature, limited active bend, accurate hand grip and foot planting.
- test_ik.cjs: retains mathematical 2-bone contact and source engine checks.
- .github/workflows/fte-smooth-limbs-v3-render.yml: render with original art and verified Kokoro voice samples.

## Audio preservation
The LOCAL finished video 'Funny_Toon_Ever_Milk_Prank_Smooth_Limbs_V3.mp4' retains the user's previous MP4 audio stream BYTE-FOR-BYTE by stream copying:
  ffmpeg -i new_silent_animation.mp4 -i user_reference_original.mp4 -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart final.mp4

The independent output QA confirmed SHA-256 of AAC audio packets matched the exact user-uploaded source MP4. This is the only way to preserve the beloved soundtrack exactly without re-encoding.

A GitHub-only reproducible render (which cannot access a private chat upload) reconstructs the Foley soundtrack and reuses previously verified Kokoro voice artifacts. Its output should not be described as audio-bit-identical to the LOCAL version without doing the same stream-copy comparison.

## Verification
Local output: 1080x1920, 24fps, 15.000s, H264 video, stereo AAC; source reference unchanged except limb silhouettes and removed joint markers. Seven decoded frame checkpoints and a Before/After contact sheet were inspected. Technical QA confirms the file is real; artistic evaluation remains subjective.

Do not re-introduce the previous V-shaped limb drawing in future iterations.
