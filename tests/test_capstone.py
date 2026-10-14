"""Offline tests for the SokoniHub cross-modal capstone. Nothing here needs
a Hugging Face download, a model call, or a live Whisper transcription:
image_tags/the .ogg.txt sidecar are this submission's declared stand-ins
for a real image/audio encoder (see README.md "Fallbacks declared").
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import analytics
import attach_transcript
import check_ethics
import check_gen_pin
import check_insights
import check_mismatch
import check_pipeline_yaml
import insights
import mismatch
import privacy_flag
import search as search_mod
import vocab_gaps
import voice_stub


# --- cosine / bag-of-words primitives ---


def test_cosine_identical_vectors_is_one() -> None:
    assert mismatch.cosine([1, 0], [1, 0]) == 1.0


def test_cosine_orthogonal_vectors_is_zero() -> None:
    assert mismatch.cosine([1, 0], [0, 1]) == 0.0


def test_cosine_zero_vector_does_not_divide_by_zero() -> None:
    assert mismatch.cosine([0, 0], [0, 0]) == 0.0


def test_tokens_lowercases_and_splits_on_punctuation() -> None:
    assert mismatch.tokens("Kiondo, bag!") == ["kiondo", "bag"]


def test_bow_counts_known_tokens_and_drops_unknown() -> None:
    v = mismatch.bow(["kiondo", "bag", "navy", "swahili"])
    assert v[mismatch.VOCAB.index("kiondo")] == 1.0
    assert v[mismatch.VOCAB.index("nike")] == 0.0
    assert sum(v) == 3.0  # "swahili" is not in VOCAB and is dropped silently


# --- score_row: the real mismatch join, and the gold pair ---


def test_score_row_clean_match_is_unflagged() -> None:
    row = {"sku": "KND-01", "title": "Sisal kiondo bag, navy trim", "image_tags": ["kiondo", "bag", "sisal", "navy", "woven"]}
    scored = mismatch.score_row(row)
    assert scored["flag"] is False


def test_score_row_gold_mismatch_is_flagged() -> None:
    row = {"sku": "NK-99", "title": "Nike tote bag, white", "image_tags": ["kiondo", "sisal", "red", "woven"]}
    scored = mismatch.score_row(row)
    assert scored["score"] == 0.0
    assert scored["flag"] is True


def test_score_row_handles_missing_tags_and_title() -> None:
    scored = mismatch.score_row({"sku": "EMPTY-01"})
    assert scored["score"] == 0.0
    assert scored["flag"] is True


def test_the_committed_catalog_matches_the_gold_pair() -> None:
    rows = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    scored = {r["sku"]: mismatch.score_row(r) for r in rows}
    assert scored["KND-01"]["flag"] is False
    assert scored["NK-99"]["flag"] is True
    assert scored["SHU-07"]["flag"] is False
    assert scored["KTG-14"]["flag"] is False


# --- check_mismatch.py: the gold check gate ---


def test_check_mismatch_passes_on_the_real_catalog() -> None:
    assert check_mismatch.main() == 0


def test_check_mismatch_fails_when_knd_01_is_wrongly_flagged(tmp_path: Path) -> None:
    report = [
        {"sku": "KND-01", "score": 0.0, "flag": True},
        {"sku": "NK-99", "score": 0.0, "flag": True},
    ]
    report_path = tmp_path / "mismatch_report.json"
    report_path.write_text(json.dumps(report))
    assert check_mismatch.main(report_path=report_path) == 1


def test_check_mismatch_recomputes_when_report_is_missing(tmp_path: Path) -> None:
    missing_report = tmp_path / "does_not_exist.json"
    assert check_mismatch.main(report_path=missing_report) == 0


# --- voice_stub.py / attach_transcript.py ---


def test_transcribe_seller_note_reads_the_sidecar(tmp_path: Path) -> None:
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    (audio_dir / "demo.ogg.txt").write_text("Navy sisal kiondo, handmade.")
    assert voice_stub.transcribe_seller_note(str(audio_dir / "demo.ogg")) == "Navy sisal kiondo, handmade."


def test_transcribe_seller_note_missing_audio_returns_empty_string(tmp_path: Path) -> None:
    assert voice_stub.transcribe_seller_note(str(tmp_path / "missing.ogg")) == ""


def test_the_committed_sidecar_attaches_to_knd_01_only() -> None:
    rows = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    attached = {r["sku"]: r["transcript"] for r in attach_transcript.attach(rows)}
    assert attached["KND-01"] != ""
    assert attached["NK-99"] == ""


def test_attach_transcript_copies_rows_instead_of_mutating() -> None:
    rows = [{"sku": "KND-01", "title": "x"}]
    attached = attach_transcript.attach(rows)
    assert "transcript" not in rows[0]
    assert "transcript" in attached[0]


# --- insights.py / check_insights.py ---


def test_insight_flagged_message_is_at_least_twenty_chars() -> None:
    out = insights.insight({"sku": "NK-99"}, {"score": 0.0, "flag": True})
    assert len(out["seller_message"]) >= 20


def test_insight_unflagged_message_has_no_overclaim_words() -> None:
    out = insights.insight({"sku": "KND-01"}, {"score": 1.0, "flag": False})
    msg = out["seller_message"].lower()
    assert "verified" not in msg
    assert "authentic" not in msg


def test_check_insights_passes_on_the_real_insights_file() -> None:
    assert check_insights.main() == 0


def test_check_insights_fails_on_overclaim(tmp_path: Path) -> None:
    path = tmp_path / "insights.json"
    path.write_text(json.dumps([
        {"sku": "KND-01", "score": 1.0, "flag": False, "seller_message": "This photo is verified and authentic."},
    ]))
    assert check_insights.main(path) == 1


# --- hf_pipeline.yaml / gen pin gates ---


def test_check_pipeline_yaml_passes() -> None:
    assert check_pipeline_yaml.main() == 0


def test_check_gen_pin_passes() -> None:
    assert check_gen_pin.main() == 0


# --- analytics.py: rates with n ---


def test_rates_overall_matches_one_flag_in_four() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    report = [mismatch.score_row(r) for r in catalog]
    out = analytics.rates(catalog, report)
    assert out["overall"]["n"] == 4
    assert out["overall"]["n_flagged"] == 1
    assert out["overall"]["flag_rate"] == 0.25


# --- search.py ---


def test_search_top_result_matches_the_query() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    results = search_mod.search("navy sisal kiondo", catalog, k=2)
    assert results[0][1] == "KND-01"


# --- vocab_gaps.py ---


def test_vocab_gaps_flags_words_outside_the_fixed_vocab() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    g = vocab_gaps.gaps(catalog)
    tokens_found = {row["token"] for row in g}
    assert "sneakers" in tokens_found


# --- privacy_flag.py ---


def test_needs_privacy_review_false_for_the_real_catalog() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    assert all(not privacy_flag.needs_privacy_review(r.get("image_tags")) for r in catalog)


def test_needs_privacy_review_true_for_person_tag() -> None:
    assert privacy_flag.needs_privacy_review(["bag", "person"]) is True


# --- check_ethics.py ---


def test_check_ethics_passes_on_the_real_note() -> None:
    assert check_ethics.main() == 0
