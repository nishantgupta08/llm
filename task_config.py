"""
task_config.py

Centralized configuration for all tasks, parameters, and UI components.
This file consolidates all task-related configurations in one place.
"""

from models_config import ENCODER_ONLY_MODELS, DECODER_ONLY_MODELS, ENCODER_DECODER_MODELS

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