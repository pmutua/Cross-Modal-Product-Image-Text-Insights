# Week 10 Capstone: Cross-Modal Product Image + Text Insights (SokoniHub)

## Overview

SokoniHub listing photo + title/description, joined and scored: each of
the four catalog rows gets a cosine agreement score between its
`image_tags` (sidecar stand-in for an image encoder) and its title, a
flag below `THRESHOLD = 0.25`, and a seller-readable review message.
`KND-01` is a clean match; `NK-99` is the teaching mismatch (Nike-titled
tote carrying kiondo/sisal tags); `SHU-07` and `KTG-14` are the two
additional SKUs. Optional: one seller voice-note sidecar
(`audio/knd-01.ogg.txt`) and one stub still-life generation for `KND-01`
with full provenance.

If you only have two SKUs, say so: **this catalog has four** —
`KND-01`, `NK-99`, `SHU-07`, `KTG-14`. If you used tags instead of CLIP,
say so: **yes, this submission scores `image_tags`, not a live CLIP
embedding** — see "Encoder honesty" below.

## Encoder honesty

- `encoder_pin.json`: `encoder_id: lab-bow-v1`, `source: lab`,
  `revision: sidecar-tags`, `honesty: sidecar-tags`.
- Did transformers run? **No.** `mismatch_report.json` and
  `insights.json` come from `mismatch.py`'s bag-of-words cosine over
  `image_tags`, not a Hugging Face Hub download. `hf_pipeline.yaml`
  names the live model this would use (`openai/clip-vit-base-patch32`)
  and `pipeline_smoke.py` (`LIVE_HF=1`) would attempt it if
  `transformers`/`torch` were installed; `encode_cache.json` records the
  `offline-stub` mode this submission actually ran in.

## Join

- Run `python mismatch.py` then `python check_mismatch.py`.
- Gold pair result: `KND-01` score 0.894 (flag `false`), `NK-99` score
  0.0 (flag `true`). `SHU-07` (0.8165) and `KTG-14` (0.75) are also
  unflagged.

## Insights

- Path: `insights.json`, written by `python insights.py` (run
  `attach_transcript.py` first if you want the `KND-01` transcript
  carried through).
- Per SKU: `score`, `flag`, `seller_message` (template sentence, no
  silent title rewrite anywhere in the code), optional `transcript`.
- Gate: `python check_insights.py`.

## Tools

- `hf_pipeline.yaml`: `feature-extraction` / `openai/clip-vit-base-patch32`
  / `revision: main` / `device: cpu`. Checked by `check_pipeline_yaml.py`.
- Generation: **stub**, not DALL-E or Stable Diffusion live. Provenance
  path: `prompts/gen/kiondo_navy_stilllife_v1.txt` → `gen_pin.json`
  (sha256 pin, written by `write_gen_pin.py`, checked by
  `check_gen_pin.py`) → `stub_render.py` → `outputs/knd-01_stub.png` +
  `outputs/knd-01_meta.json` (`not_a_photo_of_the_sku: true`).
  `gen_twin.json` names the OSS twin (Stable Diffusion) for the managed
  path (DALL-E). See `tool_card.md` for the full job/tool/file map.

## Analytics

- `rates.json` (run `python analytics.py` after `mismatch.py`): bags
  n=2 flag_rate 0.5, shoes n=1 flag_rate 0.0, textiles n=1 flag_rate
  0.0, **overall n=4 flag_rate 0.25**.
- `search.py`: query → top-k SKUs over the same bag-of-words cosine; toy
  recall@1 = 2/2 on its two demo queries (n=2, teaching sample, not a
  claim about retrieval at scale).
- `vocab_gaps.json` (`python vocab_gaps.py`): title tokens the 15-word
  `VOCAB` drops — `trim`, `sneakers`, `wrap`, `print`.

## Ethics

- [`ethics_note.md`](ethics_note.md): four required headings (who is in
  the photos, whose language, generated pixels, review path) plus a
  manager-readable risk/mitigation paragraph and a transfer note.
- Review path in one sentence: a flag routes to a human seller/moderator
  queue via `seller_message`; nothing here auto-rewrites a title or
  auto-removes a listing.
- Gate: `python check_ethics.py`.

## Fallbacks declared

- [x] no GPU / no transformers — `lab-bow-v1` bag-of-words over
  `image_tags` scored everything in this submission; `hf_pipeline.yaml`
  + `pipeline_smoke.py` are the documented live-CLIP path, not run.
- [x] no OpenAI image key / no Diffusers — `stub_render.py` writes the
  same meta JSON a live DALL-E/SD call would, plus a trivial real PNG,
  never a faked "real" render.
- [x] no Whisper — `audio/knd-01.ogg.txt` sidecar via `voice_stub.py`.
- [x] n is a teaching slice — four SKUs; every rate in `rates.json`
  carries its `n` alongside the percentage.

## Checklist

- [x] `NK-99` flagged, `KND-01` clear (`check_mismatch.py` exits 0)
- [x] `outputs/` (generated stub pixels) kept out of `images/` (gold set)
- [x] no "unhackable"/"verified"/"authentic" claims anywhere in the code
  or docs (`check_insights.py`, `check_ethics.py` both gate on this)
- [x] Weeks 5/7/8/9 reuse documented: Week 5's CLIP/dual-encoder and
  retrieval pattern is this submission's `search.py` and the declared
  (unused) live-CLIP path in `hf_pipeline.yaml`; Week 7's payday/cost
  discipline is why nothing here re-embeds on every page view — batch
  the join (`mismatch.py`), cache the result (`mismatch_report.json`),
  keep interactive reads on the cached file; Week 8's pin discipline
  (`check_prompt_pin.py`-style gates) is this submission's
  `encoder_pin.json`/`gen_pin.json` + their `check_*.py` gates; Week 9's
  Kenya DPA/privacy-review-path habits are `privacy_flag.py`'s
  `person`/`face`/`child` check and the ethics note's review-path and
  transfer sections.

## Run it yourself

```powershell
python mismatch.py
python check_mismatch.py
python attach_transcript.py
python insights.py
python check_insights.py
python voice_stub.py
python analytics.py
python search.py
python vocab_gaps.py
python privacy_flag.py
python check_pipeline_yaml.py
python write_gen_pin.py
python check_gen_pin.py
python stub_render.py
python check_ethics.py
python verify_setup.py
```

Run the offline tests:

```powershell
python -m pytest tests -q
```

## What this repo can and cannot run offline

Every file here runs fully offline: no model call, no API key, no
Hugging Face download, no Docker. `image_tags` in `catalog.json` stand
in for a real image encoder, and `audio/knd-01.ogg.txt` stands in for
live Whisper transcription. `encoder_pin.json` names this honestly
(`source: "lab"`, `revision: "sidecar-tags"`) rather than claiming a Hub
model that was never downloaded. No real catalog photos, buyer selfies,
or seller personal data are used; every SKU and transcript here is a
hand-built teaching fixture, separate from any AfyaPlus triage fixture.
