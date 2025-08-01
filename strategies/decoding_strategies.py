from enum import Enum
from dataclasses import dataclass
from typing import Union, Literal
from strategies.types import InputType, ValueType


@dataclass
class DecodingParam:
    """
    Represents a decoding parameter that influences model generation.
    """
    name: str
    label: str
    type: InputType
    value_type: ValueType
    min: Union[int, float, None]
    max: Union[int, float, None]
    ideal: Union[int, float, bool]
    info: str
    range: str = ""
    ideal_value_reason: str = ""  # Reason for the chosen ideal value

    def with_overrides(self, **kwargs) -> "DecodingParam":
        return DecodingParam(**{**self.__dict__, **kwargs})


# Universal parameters
TEMPERATURE = DecodingParam(
    "temperature", "Temperature", InputType.SLIDER, ValueType.FLOAT,
    0.0, 1.5, 0.7,
    "Controls randomness. Higher = more creative output. Use 0.1-0.3 for factual tasks, 0.7-1.0 for creative tasks.",
    "0.0 – 1.5",
    "A temperature of 0.7 provides a good balance between creativity and coherence for most tasks."
)

TOP_K = DecodingParam(
    "top_k", "Top-K", InputType.SLIDER, ValueType.INT,
    0, 100, 50,
    "Sample from top K most probable tokens. Lower values (10-20) for focused output, higher (40-50) for diversity.",
    "0 – 100",
    "Top-K of 50 allows sufficient diversity while maintaining high-quality token selection."
)

TOP_P = DecodingParam(
    "top_p", "Top-p (Nucleus Sampling)", InputType.SLIDER, ValueType.FLOAT,
    0.0, 1.0, 0.95,
    "Sample from tokens with cumulative probability ≥ p. 0.9-0.95 for balanced output, 0.8-0.9 for more focused results.",
    "0.0 – 1.0",
    "A value of 0.95 captures 95% of the probability mass, ensuring high-quality tokens while allowing some diversity."
)

REPETITION_PENALTY = DecodingParam(
    "repetition_penalty", "Repetition Penalty", InputType.SLIDER, ValueType.FLOAT,
    1.0, 2.0, 1.1,
    "Discourages repeated phrases. >1.0 penalizes repetition.",
    "1.0 – 2.0",
    "A penalty of 1.1 mildly discourages repetition without overly constraining the model's natural flow."
)

LENGTH_PENALTY = DecodingParam(
    "length_penalty", "Length Penalty", InputType.SLIDER, ValueType.FLOAT,
    0.0, 2.0, 1.0,
    "Controls preference for longer vs shorter output.",
    "0.0 – 2.0",
    "A value of 1.0 treats all lengths equally, allowing the model to choose the most appropriate response length."
)

NO_REPEAT_NGRAM_SIZE = DecodingParam(
    "no_repeat_ngram_size", "No Repeat N-Gram Size", InputType.SLIDER, ValueType.INT,
    0, 10, 2,
    "Ensures no repeated phrases of this size.",
    "0 – 10",
    "A size of 2 prevents immediate repetition of bigrams while allowing natural language patterns."
)

MAX_LENGTH = DecodingParam(
    "max_length", "Max Output Length", InputType.SLIDER, ValueType.INT,
    50, 2048, 512,
    "Maximum number of tokens to generate.",
    "50 – 2048",
    "512 tokens provide sufficient length for detailed responses while preventing overly long outputs."
)

NUM_BEAMS = DecodingParam(
    "num_beams", "Beam Width", InputType.SLIDER, ValueType.INT,
    1, 10, 4,
    "Number of beams in beam search. Higher = better quality but slower.",
    "1 – 10",
    "4 beams offer a good balance between generation quality and computational efficiency."
)

EARLY_STOPPING = DecodingParam(
    "early_stopping", "Early Stopping", InputType.CHECKBOX, ValueType.BOOL,
    None, None, True,
    "Stop generation early if all beams reach end token.",
    "",
    "Early stopping prevents unnecessary computation and ensures all beams complete naturally."
)

# Task-specific parameter selection
TASK_DECODING_PARAMS: dict[str, list[DecodingParam]] = {
    "RAG-based QA": [
        TEMPERATURE.with_overrides(ideal=0.3, ideal_value_reason="Lower temperature ensures factual, consistent responses for RAG."),
        TOP_K.with_overrides(ideal=20, ideal_value_reason="Focused token selection improves answer accuracy."),
        TOP_P.with_overrides(ideal=0.9, ideal_value_reason="Tighter nucleus sampling for more precise answers."),
        REPETITION_PENALTY.with_overrides(ideal=1.2, ideal_value_reason="Higher penalty prevents redundant information in answers."),
        NO_REPEAT_NGRAM_SIZE.with_overrides(ideal=3, ideal_value_reason="Prevents repetition of phrases in factual responses."),
    ],
    "Normal QA": [
        TEMPERATURE.with_overrides(ideal=0.5, ideal_value_reason="Balanced temperature for conversational yet accurate QA."),
        TOP_K.with_overrides(ideal=40, ideal_value_reason="Moderate diversity for natural conversation flow."),
        TOP_P.with_overrides(ideal=0.92, ideal_value_reason="Good balance between coherence and variety."),
        NUM_BEAMS.with_overrides(ideal=5, ideal_value_reason="Higher beam count improves answer quality."),
        EARLY_STOPPING.with_overrides(ideal=True, ideal_value_reason="Ensures complete, natural responses."),
    ],
    "Summarisation": [
        TEMPERATURE.with_overrides(ideal=0.5, ideal_value_reason="Lower temperature ensures factual, concise summaries."),
        TOP_K.with_overrides(ideal=30, ideal_value_reason="Focused selection for coherent summary generation."),
        TOP_P.with_overrides(ideal=0.9, ideal_value_reason="Tight nucleus sampling for precise summarization."),
        MAX_LENGTH.with_overrides(ideal=256, ideal_value_reason="Appropriate length for comprehensive yet concise summaries."),
        LENGTH_PENALTY.with_overrides(ideal=1.2, ideal_value_reason="Slightly favors longer summaries for completeness."),
        NUM_BEAMS.with_overrides(ideal=6, ideal_value_reason="Higher beam count ensures high-quality summaries."),
        EARLY_STOPPING.with_overrides(ideal=True, ideal_value_reason="Prevents incomplete summaries."),
    ],
    "Creative Writing": [
        TEMPERATURE.with_overrides(ideal=1.1, ideal_value_reason="Higher temperature encourages creative and diverse output."),
        TOP_K.with_overrides(ideal=80, ideal_value_reason="High diversity for creative expression."),
        TOP_P.with_overrides(ideal=1.0, ideal_value_reason="Full nucleus sampling maximizes creativity."),
        REPETITION_PENALTY.with_overrides(ideal=1.05, ideal_value_reason="Minimal penalty allows natural creative flow."),
        NO_REPEAT_NGRAM_SIZE.with_overrides(ideal=1, ideal_value_reason="Minimal constraint for creative expression."),
    ],
}
