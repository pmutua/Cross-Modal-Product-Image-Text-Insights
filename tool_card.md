# Tool card

| Job | Hugging Face | DALL-E | Stable Diffusion | Our file |
|---|---|---|---|---|
| Encode image/text | CLIP pipeline / `feature-extraction` | n/a | n/a | `encoder_pin.json`, `mismatch.py`, `hf_pipeline.yaml` |
| ASR voice note | Whisper ASR pipeline | n/a | n/a | `voice_stub.py`, `audio/*.txt` |
| Generate ad pixels | Diffusers (SD) | Images API | Diffusers checkpoint | `prompts/gen/`, `gen_pin.json`, `outputs/*_meta.json`, `gen_twin.json` |

All three rows ran in **fallback mode** in this submission (no GPU, no
transformers install, no OpenAI image key) — see the README's
"Fallbacks declared" checklist and `encoder_pin.json` / `outputs/*_meta.json`
for the honest provenance of what actually scored and rendered.
