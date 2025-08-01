from enum import Enum
from dataclasses import dataclass
from typing import Union, List, Dict
from strategies.types import InputType, ValueType

@dataclass
class EncodingParam:
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
    range: str = ""

    def with_overrides(self, **kwargs) -> "EncodingParam":
        return EncodingParam(**{**self.__dict__, **kwargs})


# ----------------------------
# Core Encoding Parameters
# ----------------------------

POOLING = EncodingParam(
    name="pooling",
    label="Pooling Strategy",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="mean",
    options=["mean", "max", "cls", "sum"],
    info="How to pool token embeddings into a single vector representation. Use 'mean' for average context, 'max' for highlighting strongest signal, or 'cls' for [CLS] token.",
    range="['mean', 'max', 'cls', 'sum']",
    ideal_value_reason="Mean pooling offers robust average representation and is compatible with most encoder models."
)

NORMALIZE = EncodingParam(
    name="normalize",
    label="Normalize Embeddings",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Whether to L2-normalize embeddings, which is recommended when using cosine similarity in retrieval.",
    ideal_value_reason="L2 normalization standardizes vector magnitudes, improving retrieval quality."
)

DEVICE = EncodingParam(
    name="device",
    label="Device",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="auto",
    options=["auto", "cpu", "cuda"],
    info="Device to run encoding on: 'cpu', 'cuda' (GPU), or 'auto' to auto-select.",
    range="['auto', 'cpu', 'cuda']",
    ideal_value_reason="Auto allows the system to leverage available GPU, ensuring best speed."
)

BATCH_SIZE = EncodingParam(
    name="batch_size",
    label="Batch Size",
    type=InputType.NUMBER,
    value_type=ValueType.INT,
    ideal=32,
    min_value=1,
    max_value=256,
    step=1,
    info="Number of samples to encode at once (increase for faster performance if enough memory).",
    range="1-256",
    ideal_value_reason="32 is a common default balancing speed and memory usage."
)

FP16 = EncodingParam(
    name="fp16",
    label="Use FP16 Precision",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=False,
    info="If true, use float16 precision for faster and more memory-efficient computation on modern GPUs.",
    ideal_value_reason="Use FP16 only if the GPU supports it and the model is compatible."
)

MAX_LENGTH = EncodingParam(
    name="max_length",
    label="Maximum Sequence Length",
    type=InputType.NUMBER,
    value_type=ValueType.INT,
    ideal=512,
    min_value=64,
    max_value=4096,
    step=64,
    info="Maximum number of tokens per sequence for encoding. Longer texts will be truncated or split.",
    range="64-4096",
    ideal_value_reason="512 tokens covers most use-cases and fits within most model limits."
)

TRUNCATION = EncodingParam(
    name="truncation",
    label="Enable Truncation",
    type=InputType.CHECKBOX,
    value_type=ValueType.BOOL,
    ideal=True,
    info="Whether to truncate texts longer than max_length. If false, may throw an error or require splitting.",
    ideal_value_reason="Truncation prevents errors and ensures model compatibility for long texts."
)

TOKENIZER = EncodingParam(
    name="tokenizer",
    label="Tokenizer Type",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="default",
    options=["default", "fast", "slow", "custom"],
    info="Select tokenizer (default, fast, slow, custom) if multiple available for the model.",
    range="['default', 'fast', 'slow', 'custom']",
    ideal_value_reason="Default is typically optimized for speed and compatibility."
)

RETURN_TENSORS = EncodingParam(
    name="return_tensors",
    label="Return Tensors Type",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="pt",
    options=["pt", "np", "tf"],
    info="Format to return encoded outputs: PyTorch ('pt'), NumPy ('np'), or TensorFlow ('tf').",
    range="['pt', 'np', 'tf']",
    ideal_value_reason="PyTorch ('pt') is most widely used and integrates well with HuggingFace and vector DBs."
)


# ----------------------------
# Task to Encoding Param Mapping
# ----------------------------

TASK_ENCODING_PARAMS: Dict[str, List[EncodingParam]] = {
    "RAG-based QA": [
        POOLING.with_overrides(ideal="cls", ideal_value_reason="CLS token captures the whole sequence for retrieval."),
        NORMALIZE.with_overrides(ideal=True, ideal_value_reason="L2 normalization ensures embeddings are cosine comparable."),
        DEVICE.with_overrides(ideal="auto"),
        BATCH_SIZE.with_overrides(ideal=32),
        FP16.with_overrides(ideal=False),
        MAX_LENGTH.with_overrides(ideal=512),
        TRUNCATION.with_overrides(ideal=True),
        TOKENIZER.with_overrides(ideal="default"),
        RETURN_TENSORS.with_overrides(ideal="pt"),
    ],

    "Normal QA": [
        POOLING.with_overrides(ideal="mean", ideal_value_reason="Mean pooling gives a broad context useful for QA."),
        NORMALIZE.with_overrides(ideal=False, ideal_value_reason="Raw embedding magnitudes may encode semantic signal."),
        DEVICE.with_overrides(ideal="auto"),
        BATCH_SIZE.with_overrides(ideal=32),
        FP16.with_overrides(ideal=False),
        MAX_LENGTH.with_overrides(ideal=512),
        TRUNCATION.with_overrides(ideal=True),
        TOKENIZER.with_overrides(ideal="default"),
        RETURN_TENSORS.with_overrides(ideal="pt"),
    ],

    "Summarisation": [
        POOLING.with_overrides(ideal="mean", ideal_value_reason="Mean pooling averages sentence info for summary quality."),
        NORMALIZE.with_overrides(ideal=True, ideal_value_reason="Normalization helps compare across sentences."),
        DEVICE.with_overrides(ideal="auto"),
        BATCH_SIZE.with_overrides(ideal=16, ideal_value_reason="Smaller batch size for memory efficiency during summarization."),
        FP16.with_overrides(ideal=False),
        MAX_LENGTH.with_overrides(ideal=1024, ideal_value_reason="Longer sequences for comprehensive summarization."),
        TRUNCATION.with_overrides(ideal=True),
        TOKENIZER.with_overrides(ideal="default"),
        RETURN_TENSORS.with_overrides(ideal="pt"),
    ],
}