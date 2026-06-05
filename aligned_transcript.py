"""
Build a clean speaker transcript by aligning word-level ASR to diarization.

- Re-assigns each word to the diarization segment with maximum time overlap
  (ignores per-word speaker labels from ASR so diarization is the source of truth).
- Merges consecutive lines from the same speaker when the gap is small.
- Assumes exactly two people: maps the two dominant diarization IDs to
  Agent / Customer (more talk time = Agent). Any rare extra speaker id is
  labeled Customer.

Input: one JSON with "diarization" and "wordLevelTranscription", or two files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def dist_midpoint_to_interval(mid: float, lo: float, hi: float) -> float:
    if mid < lo:
        return lo - mid
    if mid > hi:
        return mid - hi
    return 0.0


def fmt_mm_ss(t: float) -> str:
    sec = max(0.0, t)
    m = int(sec // 60)
    s = int(round(sec % 60))
    if s == 60:
        m += 1
        s = 0
    return f"{m:02d}:{s:02d}"


def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([.,!?])", r"\1", s)
    return s


@dataclass
class DiarTurn:
    start: float
    end: float
    speaker: str
    index: int


@dataclass
class Word:
    start: float
    end: float
    text: str


def load_words(data: dict[str, Any]) -> list[Word]:
    raw = data.get("wordLevelTranscription") or []
    out: list[Word] = []
    for w in raw:
        t = str(w.get("text") or w.get("word") or "").strip()
        if not t:
            continue
        out.append(
            Word(
                start=float(w["start"]),
                end=float(w["end"]),
                text=t,
            )
        )
    out.sort(key=lambda x: x.start)
    return out


def load_diar(data: dict[str, Any]) -> list[DiarTurn]:
    raw = data.get("diarization") or []
    turns: list[DiarTurn] = []
    for i, d in enumerate(raw):
        turns.append(
            DiarTurn(
                start=float(d["start"]),
                end=float(d["end"]),
                speaker=str(d["speaker"]),
                index=i,
            )
        )
    turns.sort(key=lambda x: x.start)
    return turns


def assign_turn_index(w: Word, turns: list[DiarTurn]) -> int:
    best_i = 0
    best_o = -1.0
    for t in turns:
        o = overlap(w.start, w.end, t.start, t.end)
        if o > best_o:
            best_o = o
            best_i = t.index
    if best_o > 0:
        return best_i
    mid = 0.5 * (w.start + w.end)
    best_d = float("inf")
    for t in turns:
        d = dist_midpoint_to_interval(mid, t.start, t.end)
        if d < best_d:
            best_d = d
            best_i = t.index
    return best_i


EXPECTED_PARTY_COUNT = 2


def unique_speakers_by_duration(turns: list[DiarTurn]) -> list[tuple[str, float]]:
    dur: dict[str, float] = {}
    for t in turns:
        dur[t.speaker] = dur.get(t.speaker, 0.0) + max(0.0, t.end - t.start)
    return sorted(dur.items(), key=lambda x: -x[1])


def speaker_labels_two_party(turns: list[DiarTurn]) -> dict[str, str]:
    """
    Always expose exactly two roles: Agent + Customer.

    Top talk-time diarization id -> Agent; second -> Customer.
    Any further ids (model drift) -> Customer for display.
    """
    ranked = unique_speakers_by_duration(turns)
    if not ranked:
        return {}
    agent_spk = ranked[0][0]
    customer_spk = ranked[1][0] if len(ranked) > 1 else agent_spk
    mapping: dict[str, str] = {
        agent_spk: "Agent",
        customer_spk: "Customer",
    }
    for spk, _ in ranked[2:]:
        mapping[spk] = "Customer"
    for t in turns:
        mapping.setdefault(t.speaker, "Customer")
    return mapping


def build_rows(
    words: list[Word],
    turns: list[DiarTurn],
    label_by_speaker: dict[str, str],
) -> list[dict[str, Any]]:
    by_index: dict[int, list[Word]] = {}
    for w in words:
        idx = assign_turn_index(w, turns)
        by_index.setdefault(idx, []).append(w)

    turn_by_index = {t.index: t for t in turns}
    rows: list[dict[str, Any]] = []
    for idx in sorted(by_index.keys(), key=lambda i: turn_by_index[i].start):
        bucket = by_index[idx]
        bucket.sort(key=lambda x: x.start)
        t = turn_by_index[idx]
        text = clean_text(" ".join(x.text for x in bucket))
        if not text:
            continue
        w_start = min(x.start for x in bucket)
        w_end = max(x.end for x in bucket)
        rows.append(
            {
                "start": w_start,
                "end": w_end,
                "speaker_id": t.speaker,
                "role": label_by_speaker.get(t.speaker, t.speaker),
                "text": text,
            }
        )
    rows.sort(key=lambda r: r["start"])
    return rows


def merge_same_speaker(rows: Iterable[dict[str, Any]], gap: float) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for r in rows:
        if not merged:
            merged.append(dict(r))
            continue
        prev = merged[-1]
        if (
            prev["speaker_id"] == r["speaker_id"]
            and float(r["start"]) - float(prev["end"]) <= gap
        ):
            prev["text"] = clean_text(prev["text"] + " " + r["text"])
            prev["end"] = max(float(prev["end"]), float(r["end"]))
        else:
            merged.append(dict(r))
    return merged


def format_lines(rows: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for r in rows:
        a = fmt_mm_ss(float(r["start"]))
        b = fmt_mm_ss(float(r["end"]))
        role = r["role"]
        text = r["text"]
        lines.append(f"[{a} - {b}] {role}:\n{text}\n")
    return "\n".join(lines).strip() + "\n"


def load_combined_or_split(
    input_path: Path | None,
    diar_path: Path | None,
    words_path: Path | None,
) -> dict[str, Any]:
    if input_path:
        data = json.loads(input_path.read_text(encoding="utf-8"))
        return data
    if diar_path and words_path:
        diar = json.loads(diar_path.read_text(encoding="utf-8"))
        words = json.loads(words_path.read_text(encoding="utf-8"))
        return {
            "diarization": diar.get("diarization", diar),
            "wordLevelTranscription": words.get(
                "wordLevelTranscription", words.get("words", [])
            ),
        }
    raise ValueError("Provide --input JSON or both --diarization and --words")


def align_combined_data(
    data: dict[str, Any],
    merge_gap: float = 0.9,
    agent_speaker: str | None = None,
    strict_two: bool = False,
) -> dict[str, Any]:
    """
    Run the same alignment as the CLI on an in-memory combined payload
    (keys: diarization, wordLevelTranscription or words).

    Returns dict with keys: text (formatted transcript), lines (merged rows),
    merge_gap_seconds, warnings (list of str).
    """
    warnings: list[str] = []
    turns = load_diar(data)
    words = load_words(data)
    if not turns:
        raise ValueError("No diarization turns found.")
    ranked_spk = unique_speakers_by_duration(turns)
    n_ids = len(ranked_spk)
    if n_ids != EXPECTED_PARTY_COUNT:
        msg = (
            f"Diarization has {n_ids} distinct speaker ids "
            f"({[s for s, _ in ranked_spk]}); expected {EXPECTED_PARTY_COUNT} for two-party calls."
        )
        if strict_two:
            raise ValueError(msg)
        warnings.append(msg)
        warnings.append(
            "Treating extra ids as Customer; fix upstream diarization or use strict_two=True to fail."
        )
    if not words:
        raise ValueError(
            "No wordLevelTranscription found. "
            "Provide Groq verbose_json words or a combined JSON with wordLevelTranscription."
        )
    all_spk = {t.speaker for t in turns}
    if agent_speaker and agent_speaker in all_spk:
        label_by_speaker = {spk: "Customer" for spk in all_spk}
        label_by_speaker[agent_speaker] = "Agent"
    else:
        label_by_speaker = speaker_labels_two_party(turns)
    rows = build_rows(words, turns, label_by_speaker)
    rows = merge_same_speaker(rows, merge_gap)
    text_out = format_lines(rows)
    return {
        "text": text_out,
        "lines": rows,
        "merge_gap_seconds": merge_gap,
        "warnings": warnings,
    }


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    script_dir = Path(__file__).resolve().parent
    _load_dotenv(script_dir / ".env")

    ap = argparse.ArgumentParser(description="Align words to diarization; print clean transcript.")
    ap.add_argument(
        "--input",
        type=Path,
        help="JSON with diarization + wordLevelTranscription",
    )
    ap.add_argument("--diarization", type=Path, help="JSON with diarization array only")
    ap.add_argument("--words", type=Path, help="JSON with wordLevelTranscription (or Groq export)")
    ap.add_argument("--merge-gap", type=float, default=0.9, help="Max gap (s) to merge same speaker")
    ap.add_argument(
        "--agent-speaker",
        type=str,
        default=None,
        help="Force this speaker id as Agent (e.g. SPEAKER_00)",
    )
    ap.add_argument(
        "--strict-two",
        action="store_true",
        help=f"Exit with error if diarization has other than {EXPECTED_PARTY_COUNT} speaker ids",
    )
    ap.add_argument("-o", "--output", type=Path, default=None, help="Write transcript .txt")
    ap.add_argument("--json-out", type=Path, default=None, help="Write structured JSON")
    args = ap.parse_args()

    data = load_combined_or_split(args.input, args.diarization, args.words)
    try:
        out = align_combined_data(
            data,
            merge_gap=args.merge_gap,
            agent_speaker=args.agent_speaker,
            strict_two=args.strict_two,
        )
    except ValueError as e:
        raise SystemExit(str(e)) from e
    for w in out["warnings"]:
        print(f"Warning: {w}", file=sys.stderr)
    text_out = out["text"]
    rows = out["lines"]
    print(text_out)

    out_txt = args.output or (script_dir / "transcript_aligned.txt")
    out_txt.write_text(text_out, encoding="utf-8")
    print(f"Wrote: {out_txt}", file=sys.stderr)

    payload = {"lines": rows, "merge_gap_seconds": args.merge_gap}
    out_json = args.json_out or (script_dir / "transcript_aligned.json")
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
