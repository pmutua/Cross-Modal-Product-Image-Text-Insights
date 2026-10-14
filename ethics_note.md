# SokoniHub multimodal ethics note

## Who is in the photos

This catalog has no real marketplace photos and no faces: `image_tags`
are hand-built sidecar tags standing in for a real image encoder, not a
crawl of seller or buyer photos. `privacy_flag.py` checks every row's
tags against a `person`/`face`/`child` list before anything downstream
runs; `needs_privacy_review` is `True` for any row carrying one of those
tags. None of the four teaching SKUs trigger it today, but the check
runs unconditionally so a future, larger catalog import can't skip it
by omission.

## Whose language

`VOCAB` in `mismatch.py` is 15 English tokens. `vocab_gaps.json` lists
every title word that falls outside it — `trim`, `sneakers`, `wrap`,
`print` in this catalog alone. We will not force every title into that
15-word slice to chase a higher cosine score, and we will not silently
drop Swahili, Sheng, or other product vocabulary a real SokoniHub
catalog would carry; a low score from vocabulary coverage, not a real
mismatch, is exactly the kind of false positive `vocab_gaps.json` exists
to surface to a human reviewer.

## Generated pixels

`outputs/knd-01_stub.png` and `outputs/knd-01_meta.json` are a stub
still-life, not a photo of SKU `KND-01`: `not_a_photo_of_the_sku` is
`true` in the meta file, and the stub lives in `outputs/`, never in
`images/` next to the real (teaching) catalog photos. Generated pixels
are never used as evidence for or against a mismatch flag — `NK-99`
stays flagged on its own tag/title disagreement, regardless of what a
generated lifestyle image of a *different* SKU looks like.

## Review path

A flag from `mismatch.py` routes to a human seller or moderator queue
via the `seller_message` in `insights.json`. There is no silent title
rewrite anywhere in this codebase, and no auto-takedown triggered by a
bag-of-words score alone — a flag is a request to check the photo and
confirm or edit the title, not a removal.

## Manager summary

**Risk:** a 15-word bag-of-words encoder will both miss real mismatches
(anything phrased outside `VOCAB`) and occasionally flag a clean listing
for vocabulary reasons rather than a genuine photo/title disagreement.
**Mitigation:** every flag goes to a human review queue, not an
automated takedown or title edit; `vocab_gaps.json` and `rates.json`
(with `n`, not a bare percentage) make the encoder's blind spots visible
instead of hidden inside a single score. **What we will not claim:**
this system does not "verify" or "authenticate" a listing photo, does
not run on a live Hub CLIP model in this submission (see
`encoder_pin.json`'s honest `source: "lab"` pin), and does not generate
or place real people or children in any image.

## Transfer note

AfyaPlus's triage fixtures, pins, and review-path habits (Weeks 1-9)
informed *how* this system is built — honest encoder pins, a human
review queue instead of a silent auto-action, declared fallbacks — but
no AfyaPlus data or fixtures are mixed into this catalog. AfyaPlus
poster/leaflet multimodal work is a later, separate transfer.
