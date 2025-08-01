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

    def with_overrides(self, **kwargs) -> "EncodingParam":
        return EncodingParam(**{**self.__dict__, **kwargs})


# ----------------------------
# Core Encoding Parameters
# ----------------------------

POOLING = EncodingParam(
    name="pooling",
    label="Pooling Type",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="mean",
    options=["mean", "max", "min", "cls", "last_token", "attention"],
    info="How to aggregate token embeddings into a single vector.",
    ideal_value_reason="Mean pooling provides a stable representation by averaging token embeddings, reducing noise."
)

NORMALIZATION = EncodingParam(
    name="normalize",
    label="Normalization Method",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="none",
    options=["none", "l2", "l1", "max", "zscore", "minmax"],
    info="How to normalize the final embedding vector.",
    ideal_value_reason="Use 'none' when preserving absolute vector magnitudes matters. Use 'l2' for cosine similarity."
)

LAYER_SELECTION = EncodingParam(
    name="layer",
    label="Transformer Layer",
    type=InputType.NUMBER,
    value_type=ValueType.INT,
    ideal=-1,
    min_value=-12,
    max_value=12,
    step=1,
    info="Which transformer layer to extract embeddings from.",
    ideal_value_reason="The last layer (-1) encodes the most semantic information, but second-to-last (-2) is often more stable."
)

SCALING_METHOD = EncodingParam(
    name="scaling",
    label="Embedding Scaling",
    type=InputType.DROPDOWN,
    value_type=ValueType.STR,
    ideal="none",
    options=["none", "unit", "max_abs", "std", "log"],
    info="Post-processing strategy to scale vector magnitudes.",
    ideal_value_reason="Use 'unit' scaling when using cosine similarity downstream."
)

DROPOUT = EncodingParam(
    name="dropout",
    label="Dropout Rate",
    type=InputType.NUMBER,
    value_type=ValueType.FLOAT,
    ideal=0.1,
    min_value=0.0,
    max_value=0.5,
    step=0.05,
    info="Dropout helps regularize the encoding process during training or fine-tuning.",
    ideal_value_reason="A small dropout (0.1) adds generalization without overly distorting the encoding."
)

TEMPERATURE = EncodingParam(
    name="temperature",
    label="Temperature",
    type=InputType.NUMBER,
    value_type=ValueType.FLOAT,
    ideal=1.0,
    min_value=0.1,
    max_value=2.0,
    step=0.1,
    info="Temperature controls the sharpness of token probabilities. Lower = confident, higher = diverse.",
    ideal_value_reason="A value of 1.0 maintains original model distribution without amplifying or smoothing."
)


# ----------------------------
# Task to Encoding Param Mapping
# ----------------------------

TASK_ENCODING_PARAMS: Dict[str, List[EncodingParam]] = {
    "RAG-based QA": [
        POOLING.with_overrides(ideal="cls", ideal_value_reason="CLS token captures the whole sequence for retrieval."),
        NORMALIZATION.with_overrides(ideal="l2", ideal_value_reason="L2 normalization ensures embeddings are cosine comparable."),
        LAYER_SELECTION.with_overrides(ideal=-2, ideal_value_reason="Second-to-last layer is often more generalizable."),
        SCALING_METHOD.with_overrides(ideal="unit", ideal_value_reason="Unit scaling is helpful for vector stores."),
        DROPOUT.with_overrides(ideal=0.1),
    ],

    "Normal QA": [
        POOLING.with_overrides(ideal="mean", ideal_value_reason="Mean pooling gives a broad context useful for QA."),
        NORMALIZATION.with_overrides(ideal="none", ideal_value_reason="Raw embedding magnitudes may encode semantic signal."),
        LAYER_SELECTION.with_overrides(ideal=-1),
        TEMPERATURE.with_overrides(ideal=1.0),
    ],

    "Summarisation": [
        POOLING.with_overrides(ideal="mean", ideal_value_reason="Mean pooling averages sentence info for summary quality."),
        NORMALIZATION.with_overrides(ideal="zscore", ideal_value_reason="Z-score normalization helps compare across sentences."),
        LAYER_SELECTION.with_overrides(ideal=-1),
        DROPOUT.with_overrides(ideal=0.0, ideal_value_reason="For deterministic summarization, dropout is disabled."),
        SCALING_METHOD.with_overrides(ideal="none"),
    ],
}