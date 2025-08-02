"""
task_config.py

Centralized configuration for all tasks, parameters, and UI components.
This file consolidates all task-related configurations in one place.
"""

import json
import os
from typing import Dict, Any, Optional, List
import json

# Load models from models.json
with open('config/models.json') as f:
    models_json = json.load(f)

ENCODER_ONLY_MODELS = models_json.get("ENCODER_ONLY_MODELS", [])
DECODER_ONLY_MODELS = models_json.get("DECODER_ONLY_MODELS", [])
ENCODER_DECODER_MODELS = models_json.get("ENCODER_DECODER_MODELS", [])

# =============================================================================
# PARAMETER CONFIGURATION LOADING
# =============================================================================

def load_parameters_config() -> Dict[str, Any]:
    """Load the main parameters configuration from parameters.json."""
    try:
        with open('config/parameters.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: config/parameters.json not found. Using empty configuration.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing config/parameters.json: {e}")
        return {}

def load_task_param_overrides() -> Dict[str, Any]:
    """Load task-specific parameter overrides from task_overrides.json."""
    try:
        with open('config/task_overrides.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: config/task_overrides.json not found. Using empty configuration.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing config/task_overrides.json: {e}")
        return {}

# Load configurations at module level
PARAMETERS_CONFIG = load_parameters_config()
TASK_PARAM_OVERRIDES = load_task_param_overrides()

# =============================================================================
# PARAMETER MANAGEMENT FUNCTIONS
# =============================================================================

def get_parameter_config(param_type: str, param_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific parameter."""
    if param_type not in PARAMETERS_CONFIG:
        return None
    
    param_config = PARAMETERS_CONFIG[param_type].get(param_name)
    if param_config is None:
        return None
    
    # Create a copy to avoid modifying the original
    return param_config.copy()

def get_all_parameters_for_type(param_type: str) -> Dict[str, Any]:
    """Get all parameters for a specific type (encoding, decoding, preprocessing)."""
    return PARAMETERS_CONFIG.get(param_type, {}).copy()

def _map_param_type_to_override_key(param_type: str) -> str:
    """Map parameter type to override key format."""
    mapping = {
        "encoding_parameters": "encoding",
        "decoding_parameters": "decoding", 
        "preprocessing_parameters": "preprocessing"
    }
    return mapping.get(param_type, param_type)

def get_task_parameter_override(task_name: str, param_type: str, param_name: str) -> Optional[Dict[str, Any]]:
    """Get task-specific override for a parameter."""
    override_key = _map_param_type_to_override_key(param_type)
    task_overrides = TASK_PARAM_OVERRIDES.get(task_name, {})
    param_type_overrides = task_overrides.get(override_key, {})
    return param_type_overrides.get(param_name)

def get_parameter_with_overrides(task_name: str, param_type: str, param_name: str) -> Optional[Dict[str, Any]]:
    """Get parameter configuration with task-specific overrides applied."""
    base_config = get_parameter_config(param_type, param_name)
    if base_config is None:
        return None
    
    # Apply task-specific overrides
    override = get_task_parameter_override(task_name, param_type, param_name)
    if override:
        # Create a copy to avoid modifying the original
        config_with_overrides = base_config.copy()
        config_with_overrides.update(override)
        return config_with_overrides
    
    return base_config

def get_ideal_value(task_name: str, param_type: str, param_name: str) -> Optional[Any]:
    """Get the ideal value for a parameter in a specific task."""
    override = get_task_parameter_override(task_name, param_type, param_name)
    if override and "ideal" in override:
        return override["ideal"]
    return None

def get_ideal_value_reason(task_name: str, param_type: str, param_name: str) -> Optional[str]:
    """Get the reason for the ideal value for a parameter in a specific task."""
    override = get_task_parameter_override(task_name, param_type, param_name)
    if override and "ideal_value_reason" in override:
        return override["ideal_value_reason"]
    return None

# =============================================================================
# TASK CONFIGURATION
# =============================================================================

# For each task, define:
# - Which parameter sections to show (preprocessing, encoding, decoding)
# - Which model selectors to show (encoder, decoder, encoder_decoder)
# - Which parameter blocks to include (preprocessing, encoding, decoding)

TASK_CONFIG = {
    "RAG-based QA": {
        "ui_blocks": ["preprocessing", "encoder", "decoder"],
        "param_blocks": ["preprocessing", "encoding"],
    },
    "Normal QA": {
        "ui_blocks": ["preprocessing", "encoding", "decoding", "encoder_decoder"],
        "param_blocks": ["preprocessing", "encoding", "decoding"],
    },
    "Summarisation": {
        "ui_blocks": ["preprocessing", "encoding", "decoding", "encoder_decoder"],
        "param_blocks": ["preprocessing", "encoding", "decoding"],
    },
    # Add more tasks here if needed...
}

# Example for a possible "Custom Task"
# "Custom Task": {
#     "ui_blocks": ["preprocessing", "encoding", "decoding", "encoder", "decoder", "encoder_decoder"],
#     "param_blocks": ["preprocessing", "encoding", "decoding"],
# }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_available_tasks():
    """Get list of available task names."""
    return list(TASK_CONFIG.keys())


def get_task_config(task_name: str):
    """Get configuration for a specific task."""
    return TASK_CONFIG.get(task_name, {})


def get_task_ui_blocks(task_name: str):
    """Get UI blocks for a specific task."""
    config = get_task_config(task_name)
    return config.get("ui_blocks", [])


def get_task_param_blocks(task_name: str):
    """Get parameter blocks for a specific task."""
    config = get_task_config(task_name)
    return config.get("param_blocks", [])


def has_ui_block(task_name: str, block_name: str):
    """Check if a task has a specific UI block."""
    ui_blocks = get_task_ui_blocks(task_name)
    return block_name in ui_blocks


def has_param_block(task_name: str, block_name: str):
    """Check if a task has a specific parameter block."""
    param_blocks = get_task_param_blocks(task_name)
    return block_name in param_blocks


# =============================================================================
# TASK DESCRIPTIONS AND METADATA
# =============================================================================

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


def get_task_description(task_name: str):
    """Get description for a specific task."""
    task_info = TASK_DESCRIPTIONS.get(task_name, {})
    return task_info.get("description", "")


def get_task_icon(task_name: str):
    """Get icon for a specific task."""
    task_info = TASK_DESCRIPTIONS.get(task_name, {})
    return task_info.get("icon", "🤖")


def get_task_long_description(task_name: str):
    """Get long description for a specific task."""
    task_info = TASK_DESCRIPTIONS.get(task_name, {})
    return task_info.get("long_description", "")


# =============================================================================
# PARAMETER UTILITY FUNCTIONS
# =============================================================================

def get_task_parameters(task_name: str, param_type: str) -> Dict[str, Any]:
    """Get all parameters for a specific task and parameter type with overrides applied."""
    base_params = get_all_parameters_for_type(param_type)
    override_key = _map_param_type_to_override_key(param_type)
    task_overrides = TASK_PARAM_OVERRIDES.get(task_name, {}).get(override_key, {})
    
    # Apply overrides to base parameters
    result = {}
    for param_name, param_config in base_params.items():
        config_with_overrides = param_config.copy()
        if param_name in task_overrides:
            config_with_overrides.update(task_overrides[param_name])
        result[param_name] = config_with_overrides
    
    return result

def get_parameter_types() -> List[str]:
    """Get all available parameter types."""
    return list(PARAMETERS_CONFIG.keys())

def get_available_parameters(param_type: str) -> List[str]:
    """Get all available parameter names for a specific type."""
    return list(PARAMETERS_CONFIG.get(param_type, {}).keys())

def reload_configurations():
    """Reload both parameter configurations from JSON files."""
    global PARAMETERS_CONFIG, TASK_PARAM_OVERRIDES
    PARAMETERS_CONFIG = load_parameters_config()
    TASK_PARAM_OVERRIDES = load_task_param_overrides()

# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

# Maintain backward compatibility with existing code structure
def get_task_ui_config(task_name: str):
    """Get UI configuration in the old format for backward compatibility."""
    ui_blocks = get_task_ui_blocks(task_name)
    
    # Convert to the old format
    config = {
        "preprocessing": "preprocessing" in ui_blocks,
        "encoding": "encoding" in ui_blocks,
        "decoding": "decoding" in ui_blocks,
        "encoder": "encoder" in ui_blocks,
        "decoder": "decoder" in ui_blocks,
        "encoder_decoder": "encoder_decoder" in ui_blocks,
    }
    
    return config 
