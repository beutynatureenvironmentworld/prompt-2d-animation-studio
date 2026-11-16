# ShortGPT Super Test — ගුණාත්මකත්වය වැඩිදියුණු කිරීම සහ Creative Memory

ඔබ එවූ 4.52-second MP4 එක පරීක්ෂා කළා. Qwen3 මඟින් story scenes ජනනය කිරීමත්, SSD-1B මඟින් hallway background එක ජනනය කිරීමත් සාර්ථකයි. **නමුත් ඒ models දෙකෙන් articulated video frames නිර්මාණය වෙන්නේ නැහැ**. Foreground character එක තවම vector/PIL engine එකෙන් ඇඳෙන්නේ. දුවන චලනය එක තැනක පෙනීම, දෙපාර්ශවයේ styles නොගැළපීම සහ ඉතා කෙටි comedy timing ප්‍රධාන අඩුපාඩු.

## මේ upgrade එකෙන් සැබෑවට හදා ඇති දේ

1. **Character continuity:** settings.json තුළ shirt, skin, hair, pants, shoes වර්ණ වෙනස් කළ හැකියි. Character image එකක් upload කළ පමණින් auto-rig වෙන්නේ නැහැ.
2. **Spatial movement:** settings.json හි start_x සහ door_x වෙනස් කළ හැකියි. Actor එක දුවද්දී දොර දෙසට සැබෑ තිර-ගමනක් දැන් තිබෙනවා.
3. **Project Memory:** style.md, story_bible.md, memory.md හා skills/*.md ගොනු Qwen3ට creative reference ලෙස යොමු වෙනවා. **මෙය AI model එක retrain කරන memory එකක් නොවෙයි.** අලුත් දැනුම රඳවන්න memory.md edit කර commit කරන්න.
4. **User backgrounds:** background_toilet.png, background_school.jpg ආදී රූප assets folder එකට upload කර background_mode=assets තෝරන්න. නොමැති locations සඳහා procedural fallback. background_mode=cpu තෝරාගත් විට SSD-1B විසින් අලුත් image එකක් සාදයි; uploaded background එක render එකට යොදා නොගනී.
5. **Readable timing:** pacing=readable තෝරාගත් විට ඉතා කෙටි action/narration beats දිගු කර උපරිම තත්පර 12ක් ඇතුළත සකසයි. Voice clipping අවදානම අඩු වුණත් සම්පූර්ණයෙන් නැති නොවෙන්න පුළුවන්.
6. **Quality warnings:** output JSON එකේ quality_warnings යටතේ කතාව ඉක්මන්ද, narration දිග වැඩිද, continuity ගැටලු තියේද කියා heuristic checks පෙන්වනවා.
7. **Manual storyboard:** story_plan.json ගොනුවේ scene order එක edit කර use_story_plan=true තෝරාගත හැකියි. එවිට planner AI එක bypass වෙන බව සැලකිල්ලට ගන්න.

## Android GitHub සිට අමතර files Upload කරන සරල පියවර

1. [GitHub Asset Folder](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/tree/main/shortgpt-supertest/assets/default) විවෘත කරන්න.
2. **Add file → Upload files** තෝරා background_toilet.png වැනි නමින් පින්තූරයක් upload කර **Commit changes** කරන්න. නැත්නම් style.md, memory.md, story_bible.md, skills/comedy_timing.md, settings.json edit කරන්න.
3. [Full Local AI Workflow](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/workflows/shortgpt-full-local-ai-mp4.yml) විවෘත කරන්න.
4. **Run workflow → main** තෝරා asset_profile=default, background_mode=assets (ඔබේ පින්තූර) හෝ cpu (AI-generated පසුබිම), pacing=readable තෝරන්න.
5. Workflow එක සාර්ථක වුණාට පස්සේ **Artifacts** යටතේ MP4, verification JSON සහ AI background PNG download කරන්න.

ඔබේ GitHub repository එක public නිසා **පුද්ගලික ඡායාරූප/Secrets public assets folder එකට upload කරන්න එපා.** Current system එකේ reference_character.png ගොනුවක් තැබිය හැකි වුණත්, ඒක ස්වයංක්‍රීයව චරිත rigging බවට පරිවර්තනය කරන්නේ නැහැ.

## හොඳ prompt එකක් (සපයන actions සමඟ)

"An original teal-hoodie cartoon boy looks worried, runs across the bathroom hallway towards a toilet door on the right, knocks twice, discovers it is locked, freezes in shock and slowly recovers. One consistent hallway, only one character, readable eye movements and physical timing, no constant smiling, clear setup and punchline."

## තවම නැති advanced දේවල්

- User reference sheet එකෙන් precise body rigging/character identity extraction
- AI background එකේ objects/keypoints හඳුනාගෙන hand-to-door contact align කිරීම
- සංකීර්ණ pose interpolation සහ බොහෝ විහිළු motion types
- උසස් lip-sync, human-like TTS, sound effects සහ audio alignment
- Style consistency සඳහා ControlNet/IP-Adapter/LoRA (GPU සහ වැඩි RAM අවශ්‍ය විය හැකියි)
- ඇත්තටම රූප රාමු නිරීක්ෂණය කරන automated visual QA

**විශාල AI model එකක් පමණක් එක් කිරීමෙන් මේ සියල්ල විසඳෙන්නේ නැහැ**. ඉදිරි ප්‍රධාන අදියර animation-director / pose and prop interaction engine වැඩිදියුණු කිරීමයි.
