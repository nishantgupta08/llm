"""
helper.py

Utility functions for config loading, parameter handling, text extraction, and memory management.
"""

import os
import re
import gc
import yaml
import torch
from PyPDF2 import PdfReader
from typing import Any, Dict, Tuple, List
from langchain.schema import Document


CONFIG_PATH = os.path.dirname(__file__)


def create_documents_from_chunks(chunks: List[str], metadata: Dict[str, Any] = None) -> List[Document]:
    """
    Create LangChain Document objects from text chunks.
    
    Args:
        chunks (List[str]): Text chunks
        metadata (dict): Metadata to add to documents
    
    Returns:
        List[Document]: List of Document objects
    """
    if metadata is None:
        metadata = {}
    
    documents = []
    for i, chunk in enumerate(chunks):
        doc_metadata = metadata.copy()
        doc_metadata.update({
            "chunk_id": i,
            "chunk_size": len(chunk),
            "total_chunks": len(chunks)
        })
        documents.append(Document(page_content=chunk, metadata=doc_metadata))
    
    return documents


# -----------------------------
# Config Loader
# -----------------------------
def load_configs() -> Dict[str, Any]:
    """
    Load model configurations from YAML file.
    Returns:
        models config dict.
    """
    with open(os.path.join(CONFIG_PATH, "../config/models.yaml"), "r") as f:
        models = yaml.safe_load(f)

    def extract_size(name):
        match = re.search(r"~(\d+(\.\d+)?)([MG]?)", name)
        if not match:
            return float("inf")
        size, _, unit = match.groups()
        return float(size) * (1024 if unit == "G" else 1)

    def sort_by_size(lst):
        return sorted(lst, key=extract_size)

    models["ENCODER_ONLY_MODELS"] = sort_by_size(
        models["sentence_transformer_encoders"] + models["other_encoders"]
    )
    models["DECODER_ONLY_MODELS"] = sort_by_size(models["other_decoder_models"])
    models["ENCODER_DECODER_MODELS"] = sort_by_size(
        models["qa_tuned_models"] + models["other_encoder_decoder_models"]
    )
    return models


# -----------------------------
# Utilities
# -----------------------------
def get_text_from_file(file: Any, max_chars: int = None) -> str:
    """
    Extract text from a file object (PDF or text file), optionally truncating to max_chars.
    Args:
        file (Any): File-like object.
        max_chars (int, optional): Maximum number of characters to return.
    Returns:
        str: Extracted (and possibly truncated) text.
    """
    try:
        if hasattr(file, "type") and file.type == "application/pdf":
            text = "\n".join(
                [p.extract_text() for p in PdfReader(file).pages if p.extract_text()]
            )
        else:
            text = file.read().decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    return text[:max_chars] if max_chars else text


def clean_model_name(name: str) -> str:
    """
    Remove parenthetical details from model name for display.
    Args:
        name (str): Model name string.
    Returns:
        str: Cleaned model name.
    """
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def free_memory():
    """
    Run garbage collection and clear CUDA memory if available.
    """
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


# def filter_params(params: Dict[str, Any], allowed: set) -> Dict[str, Any]:
#     """
#     Filter a parameter dictionary to only include allowed keys.
#     Args:
#         params (dict): Parameter dictionary.
#         allowed (set): Allowed parameter keys.
#     Returns:
#         dict: Filtered parameter dictionary.
#     """
#     return {k: v for k, v in params.items() if k in allowed}
