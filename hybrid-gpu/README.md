# VidBest hybrid video workers

Start_Here.ipynb contains the worker code, three ComfyUI graphs and a ready-to-use ten-second Workshop Reaction episode. Select GPU and run the notebook. The initial job regenerates frames 48 through 95. The original sound, setup and punchline survive. Pick **ltx** for a short single-image reaction, **wan** for heavier image-to-video, or **toon** to interpolate between the pose before and after the reaction. A real GPU trial is required to establish model quality and runtime on each provider. Wan is the 480p-family 14B I2V model, configured here for a 320×512 portrait trial. The preview canvas does not promise 480p output. Duration is normalized to the exact frame window; use short windows, especially for 16-frame Toon interpolation.

## First connection

* **Kaggle interactive**: Sign in, create a Notebook, import Start_Here.ipynb, select an available GPU and enable Internet. Run All, then Save Version to retain outputs. Automatic route: save a new Kaggle API token as the repository Actions secret KAGGLE_API_TOKEN and your account handle as the Actions variable KAGGLE_USERNAME. Run the Hybrid video GPU workflow with the trial notebook default. This submits a bounded private notebook. Its printed status and output commands identify the exact kernel.
* **Colab**: Upload Start_Here.ipynb, select Runtime → Change runtime type → GPU, and Run all. The final cell offers the MP4. For a resumable Colab job, mount Drive and set output to a Drive directory, or enable R2. Use as an interactive notebook. No server is exposed.
* **Lightning Studio**: In a Studio with available free GPU credit and internet, open the same embedded notebook. Check the displayed cost in your account before starting and stop your Studio after rendering. CUDA PyTorch and ffmpeg/ffprobe must be on the runtime. The setup script uses the selected provider's existing CUDA PyTorch.
* **ZeroGPU**: Optional, only with a chosen Space whose documented Gradio API accepts your image(s) and prompt. Install gradio_client on the controller, then use --hf-space-config. Set space, api_name, model-matching inputs and output_path according to that Space's View API. Supported placeholders are $first, $last, $prompt and $seed. Choose a public endpoint you trust with those images. Rate limits or a Space going offline can interrupt a job. Presets toon-space.json and ltx-space.json target the original ToonCrafter and Lightricks distilled demo Spaces. Their availability and authentication are independent of the notebook. The LTX hosted demo uses its own distilled model; the local ComfyUI preset uses 2B v0.9.5.
* **R2**: Optional. Use an existing Standard bucket and bucket-scoped S3 credentials. On a trusted runner set R2_ENDPOINT, R2_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, or use identically named Kaggle/Colab Secrets and set USE_R2=True. Install boto3 for a standalone controller. Results are private objects under vidbest/<bundle hash>/<model>/. Keys remain outside git. Store output clips here, and download model weights from upstream or attach a prepopulated cache with VIDBEST_MODEL_CACHE arranged like ComfyUI/models. Monitor storage for free-tier limits.

## Oracle controller

Run from the repository root with an existing CPU episode and JSON array of frame ranges like hybrid-gpu/shots.json:

```sh
python3 hybrid-gpu/hybrid.py pack motion-worker/bench-final/render/short.mp4 hybrid-gpu/shots.json my-episode.zip
python3 hybrid-gpu/orchestrator.py my-episode.zip renders --model ltx
```

The second command immediately creates the CPU episode plus a self-contained interactive handoff notebook. When the Kaggle CLI is installed/authenticated, add --kaggle-user YOUR_HANDLE --wait-minutes 30 to submit and collect. Re-run with the same ZIP to resume an existing job. Completed shots stay cached. A pending or ambiguous submission is recorded locally and not automatically resubmitted. The controller can collect R2 checkpoints on any invocation. For an offline manual handoff, copy the complete renders/<bundle hash>/<model>/ directory from the notebook to the same directory on Oracle before invoking finish. Use the exact same ZIP across providers. A fresh zip can have a different hash. Coordinate one provider per job to avoid duplicate GPU use; these independent provider sessions do not share a distributed lease. Public Colab notebooks are not unattended fallback servers.

```sh
python3 hybrid-gpu/hybrid.py finish my-episode.zip renders --model ltx
```

Every GPU shot is fitted to its designated frames and checked before checkpointing. Absent shots use the CPU video. Six selected five-second ranges in a thirty-second master are supported, but choosing only two action shots uses less GPU time. Comfy's native LTX/Wan graphs derive from its official example API metadata. Toon uses the pinned DynamiCrafterWrapper and the lower-memory, standard-VAE route. CPU Actions CI installs the software and checks all graphs against registered node schemas. Model weights are downloaded only on the selected GPU worker. Real GPU throughput and commercial model terms depend on the selected weights.
