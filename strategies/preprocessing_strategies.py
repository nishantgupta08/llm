"""
preprocessing_strategies.py

Defines preprocessing parameters and maps them to NLP tasks.
"""

from dataclasses import dataclass
from typing import Union, List, Dict
from strategies.types import InputType, ValueType

@dataclass
class PreprocessingParam:
    name: str
    label: str
    type: InputType
    value_type: ValueType
    ideal: Union[int, float, bool, str]
    options: List[str] = None
    info: str = ""
    min_value: Union[int, float, None] = None
    max_value: Union[int, float, None] = None
    step: Union[int, float, None] = None
    ideal_value_reason: str = ""

    def with_overrides(self, **kwargs) -> "PreprocessingParam":
        return PreprocessingParam(**{**self.__dict__, **kwargs})


# ----------------------------
# Core Preprocessing Parameters
# ----------------------------

SPLITTER_TYPE = PreprocessingParam(
    name="splitter_type",
    label="Text Splitter",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="recursive",
    options=["recursive", "character", "token", "sentence"],
    info="Controls how the text is chunked. 'recursive' for general use, 'sentence' for narrative text, 'token' for model-specific chunks",
    ideal_value_reason="Recursive splitting adapts to document structure, providing optimal chunk sizes for most tasks."
)

CHUNK_SIZE = PreprocessingParam(
    name="chunk_size",
    label="Chunk Size",
    type=InputType.NUMBER,
    value_type=ValueType.INT,
    ideal=1000,
    min_value=100,
    max_value=3000,
    step=100,
    info="Larger chunks retain more context. 1000-1500 for RAG, 500-800 for summarization, 2000+ for detailed analysis",
    ideal_value_reason="1000 characters provide sufficient context for most retrieval tasks while staying within model token limits."
)

CHUNK_OVERLAP = PreprocessingParam(
    name="chunk_overlap",
    label="Chunk Overlap",
    type=InputType.NUMBER,
    value_type=ValueType.INT,
    ideal=200,
    min_value=0,
    max_value=500,
    step=50,
    info="Preserves continuity between chunks. 10-20% of chunk size, higher for complex documents, lower for simple text",
    ideal_value_reason="200 character overlap (20% of chunk size) ensures context continuity without excessive redundancy."
)

REMOVE_EMPTY = PreprocessingParam(
    name="remove_empty",
    label="Remove Empty Chunks",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Remove empty or whitespace-only chunks",
    ideal_value_reason="Removing empty chunks improves retrieval quality and reduces noise in downstream processing."
)

MIN_CHUNK_LENGTH = PreprocessingParam(
    name="min_chunk_length",
    label="Minimum Chunk Length",
    type=InputType.NUMBER,
    value_type=ValueType.INT,
    ideal=50,
    min_value=0,
    max_value=1000,
    step=10,
    info="Avoids overly short or meaningless chunks",
    ideal_value_reason="50 characters ensures chunks contain meaningful content while allowing flexibility for short but important sections."
)

MERGE_SMALL_CHUNKS = PreprocessingParam(
    name="merge_small_chunks",
    label="Merge Small Sections",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Combine short chunks into longer ones",
    ideal_value_reason="Merging small chunks improves context retention and reduces fragmentation in downstream tasks."
)

PRESERVE_STRUCTURE = PreprocessingParam(
    name="preserve_structure",
    label="Preserve Structure",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Retain paragraph or sentence boundaries",
    ideal_value_reason="Preserving structure maintains logical flow and improves comprehension in summarization and QA tasks."
)

ENHANCE_RETRIEVAL = PreprocessingParam(
    name="enhance_retrieval",
    label="Enhance for Retrieval",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Optimize chunks for search/retrieval engines",
    ideal_value_reason="Enhancement improves search relevance and retrieval accuracy for RAG-based applications."
)

CLEAN_TEXT = PreprocessingParam(
    name="clean_text",
    label="Clean Text",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Lowercase and normalize whitespace/punctuation",
    ideal_value_reason="Text cleaning improves model understanding and reduces tokenization inconsistencies."
)

REMOVE_SPECIAL_CHARS = PreprocessingParam(
    name="remove_special_chars",
    label="Remove Special Characters",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Remove special characters and symbols",
    ideal_value_reason="Removing special characters reduces noise and improves model comprehension of core content."
)

EXTRACT_KEY_SENTENCES = PreprocessingParam(
    name="extract_key_sentences",
    label="Extract Key Sentences",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Extract important sentences for downstream tasks",
    ideal_value_reason="Key sentence extraction improves summarization quality by focusing on the most important content."
)

# ----------------------------
# Task to Preprocessing Param Mapping
# ----------------------------

TASK_PREPROCESSING_PARAMS: Dict[str, List[PreprocessingParam]] = {
    "RAG-based QA": [
        SPLITTER_TYPE.with_overrides(ideal="recursive", ideal_value_reason="Recursive splitting adapts to document structure for better retrieval."),
        CHUNK_SIZE.with_overrides(ideal=1000, ideal_value_reason="1000 characters provide optimal context for retrieval while staying within token limits."),
        CHUNK_OVERLAP.with_overrides(ideal=200, ideal_value_reason="20% overlap ensures context continuity for accurate retrieval."),
        REMOVE_EMPTY.with_overrides(ideal=True, ideal_value_reason="Removes noise that could interfere with retrieval accuracy."),
        MIN_CHUNK_LENGTH.with_overrides(ideal=50, ideal_value_reason="Ensures chunks contain meaningful content for retrieval."),
        PRESERVE_STRUCTURE.with_overrides(ideal=True, ideal_value_reason="Maintains logical flow for better answer generation."),
        ENHANCE_RETRIEVAL.with_overrides(ideal=True, ideal_value_reason="Optimizes chunks specifically for search and retrieval performance."),
    ],

    "Normal QA": [
        SPLITTER_TYPE.with_overrides(ideal="character", ideal_value_reason="Character-based splitting provides consistent chunk sizes for QA."),
        CHUNK_SIZE.with_overrides(ideal=2000, ideal_value_reason="Larger chunks provide more context for comprehensive answers."),
        MERGE_SMALL_CHUNKS.with_overrides(ideal=True, ideal_value_reason="Improves context retention for better answer quality."),
        CLEAN_TEXT.with_overrides(ideal=True, ideal_value_reason="Ensures consistent text processing for reliable QA."),
    ],

    "Summarisation": [
        SPLITTER_TYPE.with_overrides(ideal="recursive", ideal_value_reason="Recursive splitting preserves document structure for better summaries."),
        CHUNK_SIZE.with_overrides(ideal=1500, ideal_value_reason="Larger chunks capture more context for comprehensive summarization."),
        CHUNK_OVERLAP.with_overrides(ideal=300, ideal_value_reason="Higher overlap ensures continuity in summary generation."),
        REMOVE_SPECIAL_CHARS.with_overrides(ideal=True, ideal_value_reason="Removes noise that could distract from key content."),
        EXTRACT_KEY_SENTENCES.with_overrides(ideal=True, ideal_value_reason="Focuses on important content for better summary quality."),
        PRESERVE_STRUCTURE.with_overrides(ideal=True, ideal_value_reason="Maintains logical flow for coherent summaries."),
        MIN_CHUNK_LENGTH.with_overrides(ideal=200, ideal_value_reason="Ensures sufficient content for meaningful summarization."),
    ],
}