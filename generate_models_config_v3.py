#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generate a curated models catalog (famous models + quantized variants)
from Hugging Face and save as JSON.

This version enriches fields:
- size: parsed from cardData/tags (e.g., "7B", "335M") or known keys
- trained_on: from cardData["datasets"] (list/str), if present

Requirements:
  pip install huggingface_hub>=0.14.0

Usage:
  python generate_models_config_v3.py --out models_config_famous_quant.json
"""

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from huggingface_hub import HfApi

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

DEFAULT_BNB_HINTS = [
    {"format":"bitsandbytes","bits":8,"method":"int8"},
    {"format":"bitsandbytes","bits":4,"method":"nf4"}
]

def arch_type_from_tags(tags: List[str]) -> str:
    t = set([str(x).lower() for x in (tags or [])])
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

def parse_last_modified(card) -> Optional[datetime]:
    iso = getattr(card, "lastModified", None) or getattr(card, "lastModifiedAt", None)
    if not iso:
        return None
    try:
        if isinstance(iso, str):
            return datetime.fromisoformat(iso.replace("Z", "+00:00"))
        from datetime import datetime as dt
        if isinstance(iso, dt):
            return iso if iso.tzinfo else iso.replace(tzinfo=timezone.utc)
    except Exception:
        return None

def get_downloads(card) -> int:
    val = getattr(card, "downloads", None)
    if val is None:
        val = getattr(card, "downloadsAllTime", None)
    try:
        return int(val) if val is not None else 0
    except Exception:
        return 0

def is_famous(card) -> bool:
    dl = get_downloads(card)
    lm = parse_last_modified(card)
    recency_ok = False
    if lm:
        from datetime import datetime as dt
        try:
            recency_ok = (datetime.now(timezone.utc) - lm) <= timedelta(days=RECENCY_DAYS)
        except Exception:
            recency_ok = False
    allowlisted = card.modelId in CURATED_ALLOWLIST
    return allowlisted or dl >= MIN_DOWNLOADS or recency_ok

PARAM_TAG_RE = re.compile(r'(\d+(?:\.\d+)?)([BM])(?:\b|$)', re.IGNORECASE)

def parse_params_from_tags(tags: List[str]) -> Optional[str]:
    # Look for tokens like "7B", "70B", "335M" in tags
    for t in tags or []:
        m = PARAM_TAG_RE.search(str(t))
        if m:
            num, unit = m.groups()
            unit = unit.upper()
            return f"{num}{unit}"
    return None

def extract_trained_on(card_data: dict) -> Optional[str]:
    if not isinstance(card_data, dict):
        return None
    datasets = card_data.get("datasets") or card_data.get("dataset")
    if isinstance(datasets, list):
        return ", ".join(map(str, datasets[:5]))
    if isinstance(datasets, str):
        return datasets
    # sometimes "trained_on" is given directly
    if "trained_on" in card_data and isinstance(card_data["trained_on"], (str, list)):
        if isinstance(card_data["trained_on"], list):
            return ", ".join(map(str, card_data["trained_on"]))
        return str(card_data["trained_on"])
    return None

def detect_quant_formats(name: str, tags: List[str]) -> List[dict]:
    q = []
    lower = name.lower()
    for fmt, pattern in QUANT_PATTERNS.items():
        if re.search(pattern, lower):
            q.append({"format": fmt, "repo": name})
    tset = " ".join([str(t) for t in (tags or [])]).lower()
    for fmt, pattern in QUANT_PATTERNS.items():
        if re.search(pattern, tset) and not any(d["format"] == fmt for d in q):
            q.append({"format": fmt, "repo": name})
    return q

def merge_quantizations(base_q: List[dict], new_q: List[dict]) -> List[dict]:
    out = list(base_q or [])
    seen = {(d.get("format"), d.get("repo")) for d in out}
    for d in new_q or []:
        key = (d.get("format"), d.get("repo"))
        if key not in seen:
            out.append(d)
            seen.add(key)
    return out

def add_bnb_hints_if_applicable(entry: dict):
    if entry.get("type") in {"encoder", "encoder-decoder"}:
        q = entry.setdefault("quantizations", [])
        have = {d.get("format") for d in q}
        if "bitsandbytes" not in have:
            entry["quantizations"] = q + [{"format":"bitsandbytes","bits":8,"method":"int8"},{"format":"bitsandbytes","bits":4,"method":"nf4"}]

def enrich_with_model_info(api: HfApi, entry: dict):
    """Use model_info to set size (from tags) and trained_on (from datasets in card)."""
    try:
        info = api.model_info(entry["name"])
    except Exception:
        return
    tags = getattr(info, "tags", None) or []
    card_data = getattr(info, "cardData", None) or {}

    # size
    size_guess = parse_params_from_tags(tags)
    if not size_guess:
        # try common keys in card_data
        for k in ["num_params", "num_parameters", "parameters", "parameter_count"]:
            if k in card_data:
                val = str(card_data[k])
                # normalize
                m = PARAM_TAG_RE.search(val)
                size_guess = m.group(0) if m else val
                break
    if size_guess:
        entry["size"] = size_guess

    # trained_on
    trained_on = extract_trained_on(card_data)
    if trained_on:
        entry["trained_on"] = trained_on

def build_catalog(limit_per_query: int = 100) -> dict:
    api = HfApi()
    base_models: Dict[str, dict] = {}

    # 1) Discover candidate base models
    for q in SEARCH_QUERIES:
        try:
            cards = api.list_models(search=q, limit=limit_per_query)
        except TypeError:
            cards = api.list_models(limit=limit_per_query)
            cards = [c for c in cards if q.lower() in c.modelId.lower()]
        for card in cards:
            model_id = card.modelId
            if any(re.search(pat, model_id.lower()) for pat in QUANT_PATTERNS.values()):
                continue
            if not is_famous(card):
                continue
            tags = getattr(card, "tags", None) or []
            card_data = getattr(card, "cardData", None) or {}

            entry = base_models.get(model_id) or {
                "name": model_id,
                "type": arch_type_from_tags(tags),
                "task_type": task_types_from_tags(tags),
                "size": None,
                "trained_on": None,
                "description": model_id,
                "intended_use": None,
                "source": (model_id.split("/")[0] if "/" in model_id else "unknown"),
                "license": card_data.get("license"),
                "quantizations": []
            }
            base_models[model_id] = entry

    # 2) For each base model, search for quantized forks & enrich metadata
    for model_id, entry in list(base_models.items()):
        basename = model_id.split("/")[-1]
        for fmt in QUANT_PATTERNS.keys():
            q = f"{basename} {fmt}"
            try:
                q_cards = api.list_models(search=q, limit=30)
            except TypeError:
                q_cards = api.list_models(limit=200)
                q_cards = [c for c in q_cards if basename.lower() in c.modelId.lower() and fmt in c.modelId.lower()]
            for card in q_cards:
                quant = detect_quant_formats(card.modelId, getattr(card, "tags", None) or [])
                if quant:
                    entry["quantizations"] = merge_quantizations(entry.get("quantizations", []), quant)

        add_bnb_hints_if_applicable(entry)
        # Enrich size & trained_on
        enrich_with_model_info(api, entry)

    # 3) Add curated allowlist models if absent and enrich them too
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
            enrich_with_model_info(api, base_models[name])

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
