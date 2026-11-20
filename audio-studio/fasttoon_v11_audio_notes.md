# FastToon V11 — corrected superhero sound timing

This revision fixes the *audio* of the 9-second original V10 superhero video.
The rendered video bitstream was kept identical (MD5 test),
while the soundtrack was rebuilt from the isolated Kokoro voice rather than
doubling previously mixed soundtracks.

**Frame-aligned changes:** fall whoosh starts 1.60s; hero flight 2.03s;
touchdown 4.77s (not V10's 3.93s); a short irregular fart at 5.69s,
disgust gasp at 6.16s, foot contacts 6.84 / 7.10 / 7.36 / 7.62s.
The incorrectly timed 4.0s laughter is omitted. The too-loud end
"Oh no" is muted and replaced by a subdued sigh at 8.13s.

The editable timing and action metadata lives in
`audio-studio/fasttoon_v11_action_sound_profile.json`.

**Model disclosure:** Both the official Stable Audio 3 Small SFX and Suno Bark
HF community Spaces were queried. Both returned ZeroGPU quota-exceeded errors.
No neural model-based SFX was generated or claimed. Wan2.2 TI2V is video
generation and isn't a stand-alone Foley generator; S2V can consume audio but
does not solve generating physically synchronized environmental SFX.

The actual reproducible V11 MP4 and full re-rendering Python script were
created as an in-chat downloadable ZIP. This GitHub branch retains the
action-to-sound mapping, the Kokoro/Stable Audio/Bark setup code, and the
earlier working Kokoro/Rhubarb CPU demos.

A future AI SFX replacement should use named event cues, e.g.
`'one short dry comical low fart and air puff, no speech, isolated'`,
clip it to match 5.69–6.08 seconds, and **human review before publishing**.
