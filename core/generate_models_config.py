#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generate a curated models catalog (famous models + quantized variants)
from Hugging Face and save as JSON.

Requirements:
  pip install huggingface_hub

Usage:
  python generate_models_config.py --out models_config_famous_quant.json

Notes:
- "Famous" is determined by (downloads >= MIN_DOWNLOADS) and/or (updated within RECENCY_DAYS)
  and/or being in a curated allowlist.
- Quantized variants are detected by name patterns (gguf, gptq, awq, exl2),
  and attached to the base model as "quantizations".
- This script is safe to re-run; it will produce deterministic output for the same HF state.
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

from huggingface_hub import HfApi, ModelFilter

# -----------------------------
# Tunable settings
# -----------------------------

MIN_DOWNLOADS = 50_000
RECENCY_DAYS = 540  # ~18 months

CURATED_ALLOWLIST = {
    # Encoders (embeddings)
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "intfloat/e5-large-v2",
    "BAAI/bge-large-en-v1.5",
    "Alibaba-NLP/gte-large-en-v1.5",
    "nomic-ai/nomic-embed-text-v1.5",
    "Snowflake/snowflake-arctic-embed-l",
    # Encoder-decoder
    "google/flan-t5-base",
    "google/flan-t5-large",
    "facebook/bart-large-cnn",
    "allenai/led-base-16384",
    # Decoder/chat
    "meta-llama/Llama-3-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "Qwen/Qwen2-7B-Instruct",
    "microsoft/Phi-3-mini-4k-instruct",
}

SEARCH_QUERIES = [
    # Encoders
    "sentence-transformers",
    "e5 large v2",
    "bge large en",
    "gte large en",
    "nomic embed text",
    "snowflake arctic embed",
    # Encoder-decoder
    "flan t5 base",
    "flan t5 large",
    "bart large cnn",
    "led 16384",
    # Decoder/chat
    "Llama-3 Instruct 8B",
    "Mistral-7B Instruct",
    "Mixtral-8x7B Instruct",
    "Qwen2-7B Instruct",
    "Phi-3 mini 4k instruct",
]

QUANT_PATTERNS = {
    "gguf": r"(?:^|[-_/])gguf(?:$|[-_/])|\.gguf$",
    "gptq": r"(?:^|[-_/])gptq(?:$|[-_/])",
    "awq":  r"(?:^|[-_/])awq(?:$|[-_/])",
    "exl2": r"(?:^|[-_/])exl2(?:$|[-_/])",
}

# Optional bitsandbytes hints for seq2seq / embeddings
DEFAULT_BNB_HINTS = [
    {"format":"bitsandbytes","bits":8,"method":"int8"},
    {"format":"bitsandbytes","bits":4,"method":"nf4"}
]

# -----------------------------
# Helpers
# -----------------------------

def arch_type_from_tags(tags: List[str]) -> str:
    t = set([x.lower() for x in (tags or [])])
    if {"text-embedding", "feature-extraction"} & t:
        return "encoder"
    if {"seq2seq", "text2text-generation"} & t:
        return "encoder-decoder"
    return "decoder"

def task_types_from_tags(tags: List[str]) -> List[str]:
    known = {
        "text-generation","text2text-generation","text-embedding",
        "question-answering","summarization","chat","feature-extraction",
        "fill-mask","translation"
    }
    out = [x for x in (tags or []) if x in known]
    return sorted(out)

def parse_last_modified(iso: Optional[str]) -> Optional[datetime]:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return None

def is_famous(card) -> bool:
    # Famous if downloads high OR recently updated OR in allowlist
    dl = getattr(card, "downloads", None) or 0
    lm = parse_last_modified(getattr(card, "lastModified", None))
    recency_ok = False
    if lm:
        recency_ok = (datetime.now(timezone.utc) - lm) <= timedelta(days=RECENCY_DAYS)
    allowlisted = card.modelId in CURATED_ALLOWLIST
    return allowlisted or dl >= MIN_DOWNLOADS or recency_ok

def detect_quant_formats(name: str, tags: List[str]) -> List[Dict[str, Any]]:
    q = []
    lower = name.lower()
    for fmt, pattern in QUANT_PATTERNS.items():
        if re.search(pattern, lower):
            q.append({"format": fmt, "repo": name})
    # Some repos indicate quant via tags too
    tset = " ".join(tags or []).lower()
    for fmt, pattern in QUANT_PATTERNS.items():
        if re.search(pattern, tset) and not any(d["format"] == fmt for d in q):
            q.append({"format": fmt, "repo": name})
    return q

def merge_quantizations(base_q: List[Dict[str,Any]], new_q: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    out = list(base_q or [])
    seen = {(d.get("format"), d.get("repo")) for d in out}
    for d in new_q or []:
        key = (d.get("format"), d.get("repo"))
        if key not in seen:
            out.append(d)
            seen.add(key)
    return out

def add_bnb_hints_if_applicable(entry: Dict[str,Any]):
    # For encoders and encoder-decoders, add bitsandbytes hints if none provided
    if entry.get("type") in {"encoder", "encoder-decoder"}:
        q = entry.setdefault("quantizations", [])
        have = {d.get("format") for d in q}
        if "bitsandbytes" not in have:
            entry["quantizations"] = q + DEFAULT_BNB_HINTS

# -----------------------------
# Main
# -----------------------------

def build_catalog(limit_per_query: int = 100) -> Dict[str, Any]:
    api = HfApi()
    base_models: Dict[str, Dict[str,Any]] = {}

    # 1) Discover candidate base models
    for q in SEARCH_QUERIES:
        for card in api.list_models(search=q, limit=limit_per_query):
            model_id = card.modelId
            # skip obvious quant forks as base models
            if any(re.search(pat, model_id.lower()) for pat in QUANT_PATTERNS.values()):
                continue
            if not is_famous(card):
                continue
            entry = base_models.get(model_id) or {
                "name": model_id,
                "type": arch_type_from_tags(card.tags or []),
                "task_type": task_types_from_tags(card.tags or []),
                "size": None,
                "trained_on": None,
                "description": getattr(card, "modelId", None),
                "intended_use": None,
                "source": (model_id.split("/")[0] if "/" in model_id else "unknown"),
                "license": getattr(card, "cardData", {}).get("license") if getattr(card, "cardData", None) else None,
                "quantizations": []
            }
            base_models[model_id] = entry

    # 2) For each base model, search for quantized forks
    # Heuristic: search for '<basename> gguf' etc. and collect top results
    for model_id, entry in list(base_models.items()):
        basename = model_id.split("/")[-1]
        for fmt in QUANT_PATTERNS.keys():
            q = f"{basename} {fmt}"
            for card in api.list_models(search=q, limit=30):
                # attach if repo clearly contains format pattern
                quant = detect_quant_formats(card.modelId, card.tags or [])
                if quant:
                    entry["quantizations"] = merge_quantizations(entry.get("quantizations", []), quant)

        # Add bitsandbytes hints if applicable
        add_bnb_hints_if_applicable(entry)

    # 3) Optional: add curated allowlist models if not discovered (with minimal entries)
    for name in CURATED_ALLOWLIST:
        if name not in base_models:
            base_models[name] = {
                "name": name,
                "type": "decoder",
                "task_type": [],
                "size": None,
                "trained_on": None,
                "description": name,
                "intended_use": None,
                "source": (name.split("/")[0] if "/" in name else "unknown"),
                "license": None,
                "quantizations": []
            }
            add_bnb_hints_if_applicable(base_models[name])

    # 4) Sort by org/name
    catalog = sorted(base_models.values(), key=lambda d: d["name"].lower())

    return {"models": catalog}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="models_config_famous_quant.json", help="Output JSON path")
    parser.add_argument("--limit", type=int, default=100, help="Per-query search limit")
    args = parser.parse_args()

    out = build_catalog(limit_per_query=args.limit)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote {args.out} with {len(out['models'])} models.")

if __name__ == "__main__":
    main()
