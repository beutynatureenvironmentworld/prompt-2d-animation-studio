# Independent CPU 2D animation engine audit — 2026-11-16

Scope: original funny 2D anime/ink cartoon with visible articulated fast arm/leg motion. Keep `main` and its verified InkRig workflow unchanged. All tests below were bounded GitHub Actions experiments on `experiment/iki-blender-prompt-puppet-20261116` unless otherwise stated.

| Engine / technique | Real test outcome | New generated MP4? | Verified GitHub Actions run | Best use / limitation |
| --- | --- | --- | --- | --- |
| Iki auto-rig / WebGL2 | Success; real auto-rigged official MIT sample PNG layers and 24 parameter-driven facial poses; facial-motion MP4 | Yes | [43787114551](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43787114551) | Excellent facial expressions; **not** proven to auto-rig independently moving full-body limbs from arbitrary user art |
| Blender armature | Success; real bones, changing leg rotations, editable .blend and MP4 | Yes | [43764361829](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43764361829) | Best editable articulated full-body pipeline, but CPU render cost higher |
| Line-Art Animation gait IK / SVG | Success; actual upstream MIT gait solver, 144 distinct SVG frames, original spoken audio and MP4 | Yes | [43756489257](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43756489257) | Best lightweight fast running/knee/ankle motion; requires custom character art and timing |
| Rhubarb Lip Sync | Success; v1.14 original voice analysis, A-H cue JSON, mouth-shape-driven 2D MP4 | Yes | [43764399085](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43764399085) | Dialogue and mouth shapes, not a complete skeletal motion engine |
| Synfig native vector | Success after fixing shell pipeline SIGPIPE; real native vector layers, 144 rendered frames and MP4 | Yes | [43775126959](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43775126959) | Good editable tweening and vector waypoints; more manual setup |
| Blender Grease Pencil | Success; 72 genuine Grease Pencil drawing frames, editable .blend and MP4 | Yes | [43787071822](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43787071822) | Good hand-drawn pose-to-pose expressive motion; requires actual drawn poses |
| OpenToonz / Tahoma2D on Ubuntu 24.04 APT | **Not installed**: no `opentoonz` or `tahoma2d` APT package in the runner's configured repositories; job success indicates only feasibility probe success | **No** | [43792352216](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43792352216) | Next attempt, if justified: pinned trusted upstream binary/AppImage with verified hash and licensing; do not run a lengthy source build or claim MP4 without proof |

## New combined action demo (separate feature branch)

The distinct integration experiment on `feature/fast-clear-ik-iki-rhubarb-action` has already generated a **new original 12-second 24 FPS / 288-frame MP4**, combining *real upstream Line-Art gait.ts* with independently drawn arms, knees and action poses, *24 real Iki WebGL face poses* and *Rhubarb audio-driven mouth cues*. GitHub Actions verified new source frames, video output and real IK JSON. This is **not** a full-body Iki rig, not AI diffusion and not copied RicoAnimations animation.

- [Successful complete run 43793722710](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43793722710)
- [Review-only PR #13](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/pull/13)
- Artifacts expire after **7 days**; a stable archive would need separately approved user-owned storage. Do not silently reupload prior MP4 as new.

## Recommendation and stopping criterion

The distinctive CPU approaches with available bounded GitHub Actions validation have been tested. Further reruns of the same identical clips would waste quota. Next meaningful work is **quality iteration**, not another duplicate installation: improve frame-by-frame silhouette clarity, grounded feet, punchy anticipation, elbows/wrists, timing, 2D hand-drawn acting and consistent character style. Use the existing fast-action branch as a comparison baseline while preserving main InkRig.

OpenToonz/Tahoma2D remains unverified due to missing Ubuntu 24.04 APT packages. A one-time vetted upstream prebuilt binary test is possible later if its distribution and runner compatibility are verified. No source build or paid GPU should be attempted merely to claim another engine.

**No new MP4 was generated in this audit-only run.** All linked MP4s are prior verified distinct outputs. Avoid claiming this document is a new video.
