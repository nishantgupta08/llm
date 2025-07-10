# Model Choices and Task Mapping

This document explains the model categories used in this app, their intended use cases, and the logic behind the UI and task design.

## Model Categories

- **Encoder-only models**: Used for embeddings/retrieval (e.g., BERT, RoBERTa, MiniLM)
- **Decoder-only models**: Used for text generation (e.g., GPT-2, Llama, Falcon)
- **Encoder-decoder models**: Used for generative QA and summarization (e.g., T5, FLAN-T5, BART, Pegasus, mBART)

## Task Mapping

| Task                        | Model Type           | Example Models                | Class Used           |
|-----------------------------|----------------------|-------------------------------|----------------------|
| RAG-based QA (retrieval)    | Encoder-only         | BERT, RoBERTa, MiniLM         | LangchainEncoder     |
| Normal Abstractive QA       | Encoder-decoder      | T5, FLAN-T5, BART, Pegasus    | EncoderDecoder       |
| Summarization               | Encoder-decoder      | T5, FLAN-T5, BART, Pegasus    | EncoderDecoder       |

## Notes

- T5, FLAN-T5, BART, etc. are only available for abstractive QA and summarization, not for extractive QA.
- Decoder-only models (GPT-2, Llama, etc.) are not used for QA in this app.
- For memory management, see `app.py` for details on cleanup after each submission.

## Model Lists

### ENCODER_ONLY_MODELS
```
all-MiniLM-L6-v2 (~22M)
all-mpnet-base-v2 (~110M)
paraphrase-MiniLM-L6-v2 (~22M)
sentence-transformers/all-MiniLM-L12-v2 (~33M)
sentence-transformers/all-distilroberta-v1 (~82M)
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (~33M)
distilbert-base-uncased (~66M)
bert-base-uncased (~110M)
roberta-base (~125M)
```

### DECODER_ONLY_MODELS
```
gpt2 (~124M)
gpt2-medium (~355M)
gpt2-large (~774M)
gpt2-xl (~1.5B)
openai-community/gpt2-large (~774M)
tiiuae/falcon-rw-1b (~1B)
tiiuae/falcon-7b (~7B)
mistralai/Mistral-7B-v0.1 (~7B)
mistralai/Mistral-7B-Instruct-v0.2 (~7B)
meta-llama/Llama-2-7b-hf (~7B)
meta-llama/Llama-2-13b-hf (~13B)
meta-llama/Llama-2-70b-hf (~70B)
Qwen/Qwen-7B-Chat (~7B)
google/gemma-7b (~7B)
EleutherAI/gpt-j-6B (~6B)
EleutherAI/gpt-neo-1.3B (~1.3B)
EleutherAI/gpt-neo-2.7B (~2.7B)
TheBloke/Llama-2-7B-GPTQ (Quantized, GPTQ)
TheBloke/Mistral-7B-Instruct-v0.2-GPTQ (Quantized, GPTQ)
```

### QA_TUNED_MODELS (Abstractive QA)
```
deepset/roberta-base-squad2 (~125M)
distilbert-base-cased-distilled-squad (~66M)
bert-large-uncased-whole-word-masking-finetuned-squad (~340M)
```

### OTHER_ENCODER_DECODER_MODELS
```
t5-small (~60M)
t5-base (~220M)
t5-large (~770M)
facebook/bart-base (~140M)
facebook/bart-large-cnn (~400M)
google/pegasus-xsum (~568M)
google/mt5-small (~300M)
google/mt5-base (~580M)
google/mt5-large (~1.2B)
facebook/mbart-large-50-many-to-many-mmt (~610M)
google/flan-t5-large (~780M)
```

### ENCODER_DECODER_MODELS (for summarization and abstractive QA)
This is the union of QA_TUNED_MODELS and OTHER_ENCODER_DECODER_MODELS. 