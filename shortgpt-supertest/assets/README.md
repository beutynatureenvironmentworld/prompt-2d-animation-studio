# Upload extra files to the ShortGPT SuperTest workflow

**Files in this folder are ordinary GitHub repository content.** On a public repository, do not upload private photos, proprietary images, secrets, or content you lack permission to use.

Create your own profile directory, such as \`assets/my_cartoon/\`. Profiles must use only ASCII letters, digits, underscore or hyphen.

On GitHub web: navigate to this repository path -> **Add file -> Upload files** (or edit files) -> **Commit changes**. If uploading a new profile, create a simple \`settings.json\` or \`memory.md\` first. Commit your images inside the same profile directory.

Supported files (optional):

- \`settings.json\` — shirt, skin, hair, pants, shoes hex colors and \`door_x\`/ \`start_x\` relative 0..1 geometry
- \`background_toilet.png\`, \`background_school.png\`, \`background_garden.png\`, \`background_street.png\`, \`background_office.png\`, \`background_park.png\` — user background pictures; also JPEG/WebP supported
- \`style.md\` — persistent look-and-feel, e.g. line weight, palette, mood, lighting
- \`story_bible.md\` — tone, protagonist, comedy formula, recurring locations
- \`memory.md\` — persistent user-edited creative notes from earlier videos
- \`skills/*.md\` — up to six reusable short creative writing/animation guides
- \`story_plan.json\` — optional exact JSON scenes, with actions/locations supported by the renderer

GitHub Actions -> **ShortGPT SuperTest FULL Local AI Comedy MP4** -> **Run workflow**: choose \`asset_profile\` and \`image_backend\`. \`cpu\` creates a real SSD-1B image; \`assets\` uses your uploaded location backgrounds where present and procedural drawings for missing ones (no image AI credits). New \`style.md\`, memory, colors, and layouts are honored in both paths, but existing background assets are used **only** in \`assets\` mode.

Upload a character reference sheet as \`reference_character.png\` if you want to store it for future work. **Current vector actor is NOT automatically rigged or identity-matched from that image**; current runtime honors character colors from settings.json instead.

**Memory is not automatic model training.** You must edit/commit \`memory.md\` when you want persistent creative knowledge across runs. All loaded text is treated as reference data, bounded and validated.

Image safety: <=12 MiB, <=4096×4096, <=12 megapixels; formats PNG/JPEG/WebP. No symlinks or path traversal.
