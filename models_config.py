"""
Model metadata and groupings for the application.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class ModelInfo:
    """
    Stores metadata for a language model.
    """
    name: str
    type: str  # 'encoder', 'decoder', 'encoder-decoder'
    size: str
    trained_on: str
    description: str
    intended_use: str
    source: str

# -----------------------------
# Model Definitions
# -----------------------------

# Encoder-only models
ENCODER_ONLY_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="all-MiniLM-L6-v2",
        type="encoder",
        size="22M",
        trained_on="General text",
        description="MiniLM, sentence transformer, good for embeddings.",
        intended_use="Retrieval, semantic search",
        source="sentence-transformers"
    ),
    ModelInfo(
        name="all-mpnet-base-v2",
        type="encoder",
        size="109M",
        trained_on="General text",
        description="MPNet base model, excellent for semantic similarity.",
        intended_use="Semantic search, clustering",
        source="sentence-transformers"
    ),
    ModelInfo(
        name="all-MiniLM-L12-v2",
        type="encoder",
        size="118M",
        trained_on="General text",
        description="MiniLM L12, larger version with better performance.",
        intended_use="High-quality embeddings",
        source="sentence-transformers"
    ),
    ModelInfo(
        name="paraphrase-multilingual-MiniLM-L12-v2",
        type="encoder",
        size="118M",
        trained_on="Multilingual text",
        description="Multilingual MiniLM, supports 50+ languages.",
        intended_use="Multilingual search, embeddings",
        source="sentence-transformers"
    ),
    ModelInfo(
        name="distiluse-base-multilingual-cased-v2",
        type="encoder",
        size="134M",
        trained_on="Multilingual text",
        description="DistilBERT-based multilingual model.",
        intended_use="Multilingual applications",
        source="sentence-transformers"
    ),
]

# Decoder-only models
DECODER_ONLY_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="gpt2",
        type="decoder",
        size="124M",
        trained_on="WebText",
        description="GPT-2, decoder-only, good for text generation.",
        intended_use="Text generation, completion",
        source="openai-community"
    ),
    ModelInfo(
        name="gpt2-medium",
        type="decoder",
        size="355M",
        trained_on="WebText",
        description="GPT-2 medium, larger model with better generation.",
        intended_use="Text generation, story writing",
        source="openai-community"
    ),
    ModelInfo(
        name="distilgpt2",
        type="decoder",
        size="82M",
        trained_on="WebText",
        description="Distilled GPT-2, faster and smaller.",
        intended_use="Fast text generation",
        source="openai-community"
    ),
    ModelInfo(
        name="microsoft/DialoGPT-medium",
        type="decoder",
        size="345M",
        trained_on="Reddit conversations",
        description="DialoGPT for conversational AI.",
        intended_use="Chatbots, dialogue generation",
        source="microsoft"
    ),
    ModelInfo(
        name="EleutherAI/gpt-neo-125M",
        type="decoder",
        size="125M",
        trained_on="The Pile",
        description="GPT-Neo 125M, open-source GPT-3 alternative.",
        intended_use="Text generation, completion",
        source="EleutherAI"
    ),
]

# Encoder-decoder models
ENCODER_DECODER_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="t5-base",
        type="encoder-decoder",
        size="220M",
        trained_on="Colossal Clean Crawled Corpus (C4)",
        description="T5-base, encoder-decoder, good for QA and summarization.",
        intended_use="Abstractive QA, summarization",
        source="google"
    ),
    ModelInfo(
        name="t5-small",
        type="encoder-decoder",
        size="60M",
        trained_on="Colossal Clean Crawled Corpus (C4)",
        description="T5-small, faster and lighter version.",
        intended_use="Fast QA, summarization",
        source="google"
    ),
    ModelInfo(
        name="facebook/bart-base",
        type="encoder-decoder",
        size="140M",
        trained_on="News articles",
        description="BART base model, excellent for summarization.",
        intended_use="Text summarization, generation",
        source="facebook"
    ),
    ModelInfo(
        name="facebook/bart-large-cnn",
        type="encoder-decoder",
        size="400M",
        trained_on="CNN news articles",
        description="BART fine-tuned on CNN for summarization.",
        intended_use="News summarization",
        source="facebook"
    ),
    ModelInfo(
        name="microsoft/DialoGPT-medium",
        type="encoder-decoder",
        size="345M",
        trained_on="Reddit conversations",
        description="DialoGPT for conversational responses.",
        intended_use="Conversational AI, chatbots",
        source="microsoft"
    ),
    ModelInfo(
        name="google/flan-t5-base",
        type="encoder-decoder",
        size="248M",
        trained_on="Instruction-following data",
        description="Flan-T5, instruction-tuned for better QA.",
        intended_use="Question answering, instruction following",
        source="google"
    ),
    ModelInfo(
        name="google/flan-t5-small",
        type="encoder-decoder",
        size="80M",
        trained_on="Instruction-following data",
        description="Flan-T5 small, faster instruction-tuned model.",
        intended_use="Fast QA, instruction following",
        source="google"
    ),
    ModelInfo(
        name="microsoft/DialoGPT-small",
        type="encoder-decoder",
        size="117M",
        trained_on="Reddit conversations",
        description="Smaller DialoGPT for faster responses.",
        intended_use="Fast conversational AI",
        source="microsoft"
    ),
]

# All models
MODELS: List[ModelInfo] = ENCODER_ONLY_MODELS + DECODER_ONLY_MODELS + ENCODER_DECODER_MODELS

# -----------------------------
# Utility Functions
# -----------------------------
def get_models_by_type(model_type: str) -> List[ModelInfo]:
    """
    Return a list of models matching the given type.
    """
    return [m for m in MODELS if m.type == model_type] 