## Safe Kaggle GPU connection

The GitHub Action **Hybrid video GPU** now has two explicit modes.

- **prepare** (default, needs no Kaggle secrets): create a short silent Snap2D CPU cartoon, portable GPU-shot bundle and editable notebook; upload them as GitHub Actions artifacts. This tests the handoff but does NOT run the GPU model.
- **submit** (only when explicitly chosen): do the same, or use a validated existing project-local ZIP, then submit a **private** Kaggle job with the repository variable KAGGLE_USERNAME and GitHub Secret KAGGLE_API_TOKEN. The notebook embeds the CPU bundle so there is no missing Kaggle Input dataset by default.

**සිංහල:** GitHub → Actions → Hybrid video GPU → Run workflow → mode=prepare; model=ltx; bundle=auto. මෙයින් ඔබට CPU cartoon + GPU notebook ZIP ලැබේ. Kaggle account API token එක GitHub Secrets වලටත්, account username එක GitHub Variables වලටත් දා සූදානම් කළ පසු පමණක් mode=submit තෝරන්න. Chat එකට tokens යවන්න එපා.

Kaggle quota, accelerator allocation, model license/disk requirements and job completion are NOT guaranteed. The successful CPU preparation is not a test of actual GPU model inference. Colab free sessions must be started interactively and are not part of this unattended Kaggle dispatch.
