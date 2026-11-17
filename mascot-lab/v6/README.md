# Funny Toon Ever V6 — Moon Garden, Shoulder Seam Repair & Original Reaction Foley

**වර්ණවත් නව episode එකක්** — ඔබේ Funny Toon Ever original mascot එක moon garden එකක *Wish Bell* වෙත දුවනවා, තුන් වරක් තට්ටු කරනවා, පුදුමයට පත්වෙලා ලිස්සනවා, අවසානයේ මලක් පිපෙද්දී කපටි හිනාවෙන් සතුටු වෙනවා. සාමාන්‍ය narration/TTS භාවිත කරන්නේ නැහැ.

## What is really implemented

- **Preserves permanent user mascot identity**: canonical head is extracted from `mascot-lab/config/permanent_mascot.webp`. Seven original expression modes, typically the sly toothy grin except at shock/effort/fall.
- **V5 shoulder connection repair**: In original V5, arms began at outer x=175/255, y=294 while rounded body silhouette was *inside* that edge; this left a visible broken outline/gap. V6 anchors shoulders at x=186/244, y=303 (11 px embedded in torso), changes forward arm projection slightly outward to avoid an internal chest stripe, and suppresses tiny isolated black components in strictly bounded shoulder ROIs without erasing the outer contour or applying an obvious joint ring.
- **Retains V4 fast running legs and planted feet** with no X-crossing, keeps V5 front/back arm depth switching and V4 contact-only 2-bone hand IK (bell knob is exactly (406,606)).
- **Original colorful environment**: all scenery is procedurally authored using Pillow gradients, distant hills, trees, stars, flowers and a moving enchanted bell tower. No third-party image or background asset is needed.
- **Open-source offline sound system**: ambient wind, birds, footsteps, 3 bell taps, magic sparkles, slip and soft impact. Three `OH!/WHOA!/WOW!` reaction-like **formant vowel synthesizers** plus matching small on-screen captions. These are *not human recordings or an intelligible English voice model*; they are stylized vocal-like musical sounds. No narrative voiceover and no paid API.
- **Source story prompt** in `output/STORY_PROMPT.json`; the `fte-motion-v3` 11.5-second validated timeline is reused. It is **not a Qwen3 inference result or unrestricted prompt-to-video**.
- Actual 276-frame 24fps 540×960 **H.264/AAC MP4**, original SFX, decoded-frame QA and real contact sheet.

## Reproducible GitHub Actions runner

The GitHub V6 workflow copies only the unchanged foundation modules and regression tests from `mascot-lab/v5` into the V6 isolated working directory, **without overwriting patched V6 modules**. This avoids unnecessary duplication of large assets and keeps the verified V5 production source untouched. The runner installs FFmpeg and `requirements.txt`, extracts the original mascot portrait, runs all inherited tests + new V6 tests, renders real MP4, checks H264/AAC/foot lanes/door contact and uploads video + source plan + frames + QA report as an artifact.

To try locally from repo root:

```bash
python -m pip install -r mascot-lab/v6/requirements.txt
# apt install ffmpeg (Linux); install FFmpeg by package manager on your OS
python mascot-lab/v5/src/extract_canonical.py --sheet mascot-lab/config/permanent_mascot.webp --output mascot-lab/v6/assets/canonical_neutral_pose.png
# copy missing Python source from mascot-lab/v5/src to mascot-lab/v6/src without overwriting V6 updates
python -m unittest discover -s mascot-lab/v6/tests -v
cd mascot-lab/v6
python src/v3_director.py --prompt 'The sly mascot rings the magic bell; a flower blooms' --output output/MOTION_PLAN.json
python src/render.py --plan output/MOTION_PLAN.json --sheet assets/canonical_neutral_pose.png --output output/Funny_Toon_Ever_V6_Moon_Garden.mp4
python src/quality_v6.py --video output/Funny_Toon_Ever_V6_Moon_Garden.mp4 --report output/Funny_Toon_Ever_V6_Moon_Garden.json
```

**IMPORTANT**: the copy step is needed only when the V6 directory contains only the files changed in this version. The GitHub workflow supplies it exactly.

## Verified measurements and limits

Local source-based verification: 23 tests discovered with 22 passes and one skip (test requiring the optional 6-pose source sheet in a test path), 276 frames and 24 FPS, 11.5 sec, seven face expressions; intact V4 hand contact maximum ~6.2 px; zero reported leg crossings among 276 analytic samples; world-planted stance drift zero in eligible samples; disconnected shoulder specks cleaned on the rendered source. The numbers **cannot prove artistic perfection**; shoulder shape still deserves visual feedback.

Current limitations: The limb/torso is **procedural and not extracted as full rig from the supplied reference image**. There is still a little line-art aliasing at 540×960. The 11.5-second action choreography is intentionally constrained to the approved sprint → knock → surprise → stumble → bloom beats. The user's Qwen3/SSD‑1B reasoning and image generation workflow remains separate; connecting arbitrary LLM scenes or a realistic speech model is a future optional integration.

## Copyright / privacy

Only user's original canonical mascot plus newly coded artwork and original synthesized foley are used. Do not upload private photos or any token to a public GitHub repo. No account key, model weight, or paid GPU needed. The old stable V5 remains untouched.
