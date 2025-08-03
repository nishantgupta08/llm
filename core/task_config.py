"""
task_config.py

Centralized configuration for all tasks, parameters, and UI components.
"""

import os
import json

# --- Config Paths ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(base_dir, "config")

def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found. Using empty config.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing {path}: {e}")
        return {}

models_json = _load_json(os.path.join(config_dir, "models.json"))
PARAMETERS_CONFIG = _load_json(os.path.join(config_dir, "parameters.json"))
TASK_PARAM_OVERRIDES = _load_json(os.path.join(config_dir, "task_overrides.json"))

ENCODER_ONLY_MODELS = models_json.get("ENCODER_ONLY_MODELS", [])
DECODER_ONLY_MODELS = models_json.get("DECODER_ONLY_MODELS", [])
ENCODER_DECODER_MODELS = models_json.get("ENCODER_DECODER_MODELS", [])

# --- Task Config ---
TASK_CONFIG = {
    "RAG-based QA": {
        "ui_blocks": ["preprocessing", "encoder", "decoder"],
        "param_blocks": ["preprocessing", "encoding", "decoding"],
    },
    "Normal QA": {
        "ui_blocks": ["preprocessing", "encoding", "decoding", "encoder_decoder"],
        "param_blocks": ["preprocessing", "encoding", "decoding"],
    },
    "Summarisation": {
        "ui_blocks": ["preprocessing", "encoding", "decoding", "encoder_decoder"],
        "param_blocks": ["preprocessing", "encoding", "decoding"],
    }
}

TASK_DESCRIPTIONS = {
    "RAG-based QA": {
        "description": "Retrieval-Augmented Generation for question answering using document context",
        "icon": "🔍",
        "long_description": "Upload documents and ask questions. The system will retrieve relevant context and generate answers based on the document content."
    },
    "Normal QA": {
        "description": "Direct question answering without document retrieval",
        "icon": "❓",
        "long_description": "Ask questions directly to the model without providing additional context documents."
    },
    "Summarisation": {
        "description": "Generate concise summaries of input text",
        "icon": "📝",
        "long_description": "Upload documents or input text to generate summaries of varying lengths and styles."
    }
}

# --- Utility Functions ---
def get_available_tasks():
    return list(TASK_CONFIG)

def get_task_config(task):
    return TASK_CONFIG.get(task, {})

def get_task_ui_blocks(task):
    return TASK_CONFIG.get(task, {}).get("ui_blocks", [])

def get_task_param_blocks(task):
    return TASK_CONFIG.get(task, {}).get("param_blocks", [])

def get_task_description(task):
    return TASK_DESCRIPTIONS.get(task, {}).get("description", "")

def get_task_icon(task):
    return TASK_DESCRIPTIONS.get(task, {}).get("icon", "🤖")

def get_task_long_description(task):
    return TASK_DESCRIPTIONS.get(task, {}).get("long_description", "")

def _map_param_type(param_type):
    return {"encoding_parameters": "encoding", "decoding_parameters": "decoding", "preprocessing_parameters": "preprocessing"}.get(param_type, param_type)

def get_task_parameters(task, param_type):
    base = PARAMETERS_CONFIG.get(param_type, {})
    overrides = TASK_PARAM_OVERRIDES.get(task, {}).get(_map_param_type(param_type), {})
    # Overlay overrides on base
    return {k: {**v, **overrides.get(k, {})} for k, v in base.items()}

def get_parameter_with_overrides(task, param_type, param_name):
    base = PARAMETERS_CONFIG.get(param_type, {}).get(param_name, {}).copy()
    override = TASK_PARAM_OVERRIDES.get(task, {}).get(_map_param_type(param_type), {}).get(param_name, {})
    base.update(override)
    return base

def get_ideal_value(task, param_type, param_name):
    return TASK_PARAM_OVERRIDES.get(task, {}).get(_map_param_type(param_type), {}).get(param_name, {}).get("ideal")

def get_ideal_value_reason(task, param_type, param_name):
    return TASK_PARAM_OVERRIDES.get(task, {}).get(_map_param_type(param_type), {}).get(param_name, {}).get("ideal_value_reason")

def reload_configurations():
    global PARAMETERS_CONFIG, TASK_PARAM_OVERRIDES, models_json
    PARAMETERS_CONFIG = _load_json(os.path.join(config_dir, "parameters.json"))
    TASK_PARAM_OVERRIDES = _load_json(os.path.join(config_dir, "task_overrides.json"))
    models_json = _load_json(os.path.join(config_dir, "models.json"))

# --- Old API compatibility ---
def get_task_ui_config(task):
    blocks = get_task_ui_blocks(task)
    return {k: (k in blocks) for k in ["preprocessing", "encoding", "decoding", "encoder", "decoder", "encoder_decoder"]}
