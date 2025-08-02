# 🧠 GenAI Playground

A comprehensive LLM framework with dynamic parameter configuration and task orchestration.

## 📁 Project Structure

```
llm/
├── app.py                          # Main Streamlit application
├── server.py                       # Server runner with ngrok support
├── config/                         # Configuration files
│   ├── __init__.py
│   ├── parameters.json             # Parameter definitions
│   ├── task_overrides.json         # Task-specific overrides
│   ├── models.py                   # Model configurations
│   └── tasks.py                    # Task configurations
├── core/                           # Core functionality
│   ├── __init__.py
│   ├── task_orchestrator.py        # Task execution orchestration
│   └── vectorstore.py              # Vector store management
├── components/                     # Model components
│   ├── __init__.py
│   ├── encoder.py                  # Encoder models
│   ├── decoder.py                  # Decoder models
│   ├── encoder_decoder.py          # Encoder-decoder models
│   └── preprocessor.py             # Text preprocessing
└── utils/                          # Utilities
    ├── __init__.py
    ├── core_utils.py               # Core utility functions
    └── ui_utils.py                 # UI helper functions
```

## 🚀 Quick Start

### Run the Application
```bash
# Start the Streamlit app
python server.py

# Or run directly
streamlit run app.py
```

### Development
```bash
# Install dependencies
pip install streamlit pyngrok langchain transformers torch

# Run tests
python -c "import config.tasks; print('Configuration loaded successfully')"
```

## 🔧 Configuration

### Parameters (`config/parameters.json`)
- **Encoding parameters**: Pooling strategies, normalization, device settings
- **Decoding parameters**: Temperature, top-k, max length settings
- **Preprocessing parameters**: Text splitting, chunking configurations

### Task Overrides (`config/task_overrides.json`)
- **Ideal values**: Task-specific recommended parameter values
- **Reasoning**: Explanations for why certain values work best

### Models (`config/models.py`)
- **Encoder models**: Sentence transformers, BERT variants
- **Decoder models**: GPT variants, text generation models
- **Encoder-decoder models**: T5, BART, summarization models

## 🎯 Supported Tasks

1. **RAG-based QA**: Document-based question answering
2. **Normal QA**: Direct question answering
3. **Summarization**: Text summarization

## 📊 Features

- ✅ **Dynamic parameter configuration** from JSON files
- ✅ **Task-specific ideal values** with explanations
- ✅ **Multiple model types** (encoder, decoder, encoder-decoder)
- ✅ **Real-time parameter widgets** (dropdowns, sliders, checkboxes)
- ✅ **Ngrok tunneling** for easy sharing
- ✅ **Memory management** for GPU optimization

## 🔄 Recent Changes

- **Restructured codebase** for better organization
- **Renamed files** for clarity and consistency
- **Separated utilities** into core and UI functions
- **Enhanced JSON integration** with dynamic parameter loading 