# Kaggle 30-hour-efficient 2D comedy studio

## සිංහල — වටිනාම ක්‍රමය

මෙය සතියකට අනිවාර්යයෙන් වීඩියෝ 1,200+ සාදන යන්ත්‍රයක් නොවේ. **Kaggle පැය 30** CPU rendering සඳහා භාවිත නොකර, අත්‍යවශ්‍ය GPU shots කිහිපයකට පමණක් යොදන සැලැස්මයි. Reference එකේ hand-inked stickman slapstick, over-acted faces, quick camera zooms, cuts, pose-to-pose actions CPU Snap2D මත තිබෙනවා. එකම චරිතය පවත්වාගෙන යාමට එකම authored rig එකක් වඩා හොඳයි.

### මේ repository එකෙන් දැන් කරන්න පුළුවන්

1. **CPU story + MP4**: මුලින් Snap2D vector renderer එකෙන් complete portrait video render කරන්න. එය තනි CPU GitHub workflow එකේ වැඩ කරනවා.
2. **GPU shot budget**: \`python kaggle-studio/shot_budget.py snap2d/examples/storyboard_cookie.json --out gpu-shots.json\`. මෙම code එක chase / trip වගේ වැඩි motion තියෙන shots උපරිම **දෙකක්**, එකක් 48 frames හෝ අඩුවෙන් තෝරයි.
3. **Kaggle GPU smoke**: GitHub Actions → **Kaggle efficient 2D studio** → Run workflow. **probe** තෝරන්න. NVIDIA GPU tensor calculations සහ 256×256 proof image (NOT AI diffusion) සාදා GPU availability පරීක්ෂා කරයි.
4. **පළමු AI image**: කෙටි GPU test සාර්ථක වූ විට පමණක් \`pose-ai\` තෝරන්න. Diffusers මගින් **Stable Diffusion v1.5** model (CreativeML OpenRAIL-M license, not an MIT weight) download කර **original cartoon pose image එකක්** ජනනය කරයි. Model loading සහ render එකක් පළමු වරට කාලය ගනී. මෙම code එක තවම ඔබගේ Kaggle GPU මත verify කර නැහැ.
5. **විශේෂ GPU animation**: Kaggle account/GPU සාර්ථක වූ පසු repo හි පවතින \`hybrid-gpu\` ComfyUI/LTX/ToonCrafter notebook එකේ **එක් short segment එකක්** generate කර CPU timeline එකට යොදන්න. Wan 14B T4 මත සරල short-shot fallback එකක් නොවේ.

### GitHub සම්බන්ධ කිරීම

GitHub Actions repository variable: \`KAGGLE_USERNAME\`  
GitHub Actions repository secret: \`KAGGLE_API_TOKEN\` (2026 Kaggle new-style access token).

**Secrets chat එකට එවන්න එපා.** GitHub workflow එකේ credentials තිබෙනවා නම් වෙනම PRIVATE Kaggle kernel එකක් නිර්මාණය කර GPU test එක ඉල්ලනවා. Credentials නැතිනම් කිසිම GPU quota නොවැය කර skip කරනවා. Model weights repo එකට commit කරන්නේ නැහැ.

### Local / offline tests

\`\`\`bash
python3 -m unittest discover -s kaggle-studio -p 'test_*.py' -v
python3 kaggle-studio/shot_budget.py snap2d/examples/storyboard_cookie.json --out gpu-shots.json
python3 kaggle-studio/dispatch.py --username example --mode probe --minutes 8 --job-id demo --out /tmp/vidbest-probe
\`\`\`

The local job builder defaults to **dry-run**. It never submits unless \`--submit\` is passed and a valid \`KAGGLE_API_TOKEN\` exists in the execution environment. Kaggle metadata is \`is_private=true\`, uses the current documented GPU identifier \`NvidiaTeslaT4\` (T4 ×2 when allocated), and a strict 2–30 minute timeout. Only **GPU 0** is used for the first image; VRAM on two GPUs cannot simply be added for a single model.

### Model quality and licenses

- CPU pose rigs should remain primary for character consistency, rapid actions, reuse and easy correction.
- GPU generated character stills are optional art references; using the same seed is NOT a guarantee of consistent facial identity.
- FLUX.1-Schnell has Apache 2.0 weights but is a 12B-parameter model; full precision may exceed a single T4's usable memory, so it is deliberately NOT an unconditional default. Its quantized mode would require a separate real test.
- Bria RMBG 2.0 weights are **CC BY-NC** (noncommercial); avoid them as an automatic component of a monetized workflow. Use original transparent vector rigs, licensed assets, or a separately reviewed removal model instead.
- SD1.5's CreativeML OpenRAIL-M is **not** the same as an unrestricted OSI-open-source license and carries usage restrictions. Review before commercial distribution.
- ComfyUI / LTX / Wan / ToonCrafter model requirements, weights and licences must be reviewed individually; no false 'all installed' claim.

### Genuine speed numbers require real GPU benchmarking

The statement "GPU 45–60 seconds yields one entire polished 23-second video" is **unverified**. Download time, model cold start, 2D pose coherence, retries, upscaling and CPU final output all count. **1,200–1,800 videos/week is not a measured throughput.** Kaggle official documentation says the quota is weekly and can vary; do not promise GPU is always available. Public GitHub Actions CPU usage is also subject to terms and quotas.

### Kaggle persistence and quota efficiency

- GitHub stores source/scripts/shot timelines. Store large weights outside GitHub, subject to model and platform quotas/licences.
- Use Hugging Face cache inside Kaggle or a license-compliant Kaggle Model/Dataset mount for weights; mounts and Kaggle quota are account-specific.
- Keep CPU audio, zooms, camera shake and video export out of GPU sessions.
- Stop the Kaggle kernel when the work is complete; never leave a notebook idle or expose a public ComfyUI tunnel.
- Outputs from short GPU jobs can be downloaded as private Kaggle kernel outputs, then brought into the Snap2D/FFmpeg pipeline. Optional R2 only if cross-session checkpointing is required.

### Official references

Kaggle GPU quota: https://www.kaggle.com/docs/efficient-gpu-usage  
Kaggle CLI push: https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md  
Kaggle token: https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md  
SD1.5 model license: https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5  
FLUX.1-schnell: https://huggingface.co/black-forest-labs/FLUX.1-schnell  
RMBG-2.0 noncommercial: https://huggingface.co/briaai/RMBG-2.0
