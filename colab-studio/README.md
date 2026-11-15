# VidBest Google Colab interactive GPU test + AI Horde secret check

## සිංහල — මුලින්ම කරන්න ඕන දේ

**AI Horde:** GitHub Secrets API එකෙන් ChatGPT වෙත key value කියවිය නොහැක. GitHub Actions හි \`AI_HORDE_API_KEY\` environment secret එක භාවිත කරන්නේ එහි අගය කිසිවිටක print නොකර \`GET https://aihorde.net/api/v2/find_user\` හරහා authenticate වන්නේද යන්න පරීක්ෂා කිරීමට පමණි. කිසිම AI image job එකක් මෙයින් ආරම්භ නොවේ.

**Colab පමණයි:** [Open GPU notebook in Colab](https://colab.research.google.com/github/beutynatureenvironmentworld/prompt-2d-animation-studio/blob/main/colab-studio/VidBest_Colab_2D_AI_Test.ipynb)

1. Colab විවෘත කර Google account එකෙන් sign in වෙන්න.
2. Runtime → Change runtime type → **T4 GPU** (available නම්).
3. පළමු GPU probe cell එක run කරන්න; model download එකක් සිදු නොවේ.
4. කැමති නම් \`RUN_AI_VIDEO = False\` → \`True\` කර ඉතිරි cells run කරන්න. මෙය පළමු වරට විශාල weights download කර 8-frame AI motion clip එකක් ජනනය කිරීමට උත්සාහ කරයි.
5. \`colab_ai_new_clip.mp4\` ලැබුණොත් ඒක download කර බලන්න. ලැබුණේ නැත්නම් GPU success ලෙස නොසලකන්න.

**Colab free usage:** Colab free is interactive compute; resource quota and GPU access are not guaranteed. Do NOT expose unauthenticated public ComfyUI tunnels, SSH remote controllers or use Colab to operate an unattended distributed worker. See https://research.google.com/colaboratory/faq.html.

**Model licenses:** AnimateDiff-Lightning uses CreativeML OpenRAIL-M (https://huggingface.co/ByteDance/AnimateDiff-Lightning); ToonYou base model has its own terms; assess rights before publishing commercially.

**Scope:** This is a NEW AI motion experiment, NOT proof of a rendered clip. GitHub CI validates notebook syntax and secret authentication only. Inference must be run interactively on your own free Colab runtime. Nothing is sent to Kaggle or R2, and no AI Horde generation request is made.

## English

The only GitHub secret this workflow reads is \`AI_HORDE_API_KEY\`, and it never prints that value. The authentication result is simply one of \`authenticated\`, \`missing\`, \`rejected\`, \`api_http_error\` or \`network_or_response_error\`. The notebook is public, key-free and independent of AI Horde authentication.

The short optional AnimateDiff-Lightning 4-step test creates a true animated GPU video when it succeeds, instead of relabeling a previously rendered CPU video. It may still fail on Colab's free 15GB-class GPUs, network/model availability, or library changes. This has not been remotely rendered from GitHub CI.
