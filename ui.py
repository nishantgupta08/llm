import streamlit as st
import json
from task_config import (
    get_available_tasks,
    get_task_ui_config,
    get_task_description,
    get_task_icon,
    has_ui_block,
    has_param_block,
    get_task_parameters,
    get_parameter_with_overrides,
    get_ideal_value,
    get_ideal_value_reason
)
from models_config import (
    ENCODER_ONLY_MODELS,
    DECODER_ONLY_MODELS,
    ENCODER_DECODER_MODELS
)
from utils.ui_helper import display_compact_widgets_table, model_dropdown

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

def create_parameter_widget(param_name: str, param_config: dict, task_name: str, param_category: str):
    """Create a Streamlit widget based on parameter configuration."""
    widget_type = param_config.get("type", "text")
    label = param_config.get("label", param_name)
    info = param_config.get("info", "")
    
    # Get ideal value and reason
    ideal_value = get_ideal_value(task_name, param_category, param_name)
    ideal_reason = get_ideal_value_reason(task_name, param_category, param_name)
    
    # Add info about ideal value if available
    if ideal_value is not None:
        info += f"\n\n💡 **Ideal Value**: {ideal_value}"
        if ideal_reason:
            info += f"\n**Reason**: {ideal_reason}"
    
    if info:
        st.info(info)
    
    if widget_type == "dropdown":
        options = param_config.get("options", [])
        default_index = 0
        if ideal_value and ideal_value in options:
            default_index = options.index(ideal_value)
        return st.selectbox(label, options, index=default_index)
    
    elif widget_type == "slider":
        min_val = param_config.get("min_value", 0.0)
        max_val = param_config.get("max_value", 1.0)
        step = param_config.get("step", 0.1)
        default_val = ideal_value if ideal_value is not None else min_val
        return st.slider(label, min_val, max_val, default_val, step)
    
    elif widget_type == "number":
        min_val = param_config.get("min_value", 0)
        max_val = param_config.get("max_value", 100)
        step = param_config.get("step", 1)
        default_val = ideal_value if ideal_value is not None else min_val
        return st.number_input(label, min_val, max_val, default_val, step)
    
    elif widget_type == "checkbox":
        default_val = ideal_value if ideal_value is not None else False
        return st.checkbox(label, default_val)
    
    else:  # text input
        default_val = ideal_value if ideal_value is not None else ""
        return st.text_input(label, default_val)

def display_parameters_section(task_name: str, param_type: str):
    """Display parameters for a specific type with JSON configuration."""
    # Get parameters from JSON configuration
    parameters = get_task_parameters(task_name, param_type)
    
    if not parameters:
        st.info(f"No {param_type} parameters configured for this task.")
        return {}
    
    st.subheader(f"📋 {param_type.replace('_', ' ').title()}")
    
    user_params = {}
    for param_name, param_config in parameters.items():
        with st.expander(f"⚙️ {param_config.get('label', param_name)}"):
            value = create_parameter_widget(param_name, param_config, task_name, param_type)
            user_params[param_name] = value
    
    return user_params

# Get available tasks
available_tasks = get_available_tasks()

# Task selection with icons and descriptions
st.sidebar.header("🎯 Task Selection")
task = st.sidebar.radio(
    "Choose task:",
    available_tasks,
    format_func=lambda x: f"{get_task_icon(x)} {x}"
)

# Display task description
task_description = get_task_description(task)
if task_description:
    st.sidebar.info(f"**{task}**: {task_description}")

# Get task configuration
cfg = get_task_ui_config(task)
user_params = {}

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 Configuration")
    
    # Display parameters from JSON configuration
    if has_param_block(task, "preprocessing"):
        preprocessing_params = display_parameters_section(task, "preprocessing_parameters")
        if preprocessing_params:
            user_params["preprocessing"] = preprocessing_params

    if has_param_block(task, "encoding"):
        encoding_params = display_parameters_section(task, "encoding_parameters")
        if encoding_params:
            user_params["encoding"] = encoding_params

    if has_param_block(task, "decoding"):
        decoding_params = display_parameters_section(task, "decoding_parameters")
        if decoding_params:
            user_params["decoding"] = decoding_params

with col2:
    st.header("🎛️ Model Selection")
    
    # Model selection blocks
    if has_ui_block(task, "encoder"):
        encoder_name = model_dropdown(
            "Encoder Model", 
            ENCODER_ONLY_MODELS, 
            task=task
        )
        user_params["encoder"] = encoder_name

    if has_ui_block(task, "decoder"):
        decoder_name = model_dropdown(
            "Decoder Model", 
            DECODER_ONLY_MODELS, 
            task=task
        )
        user_params["decoder"] = decoder_name

    if has_ui_block(task, "encoder_decoder"):
        encdec_name = model_dropdown(
            "Encoder-Decoder Model", 
            ENCODER_DECODER_MODELS, 
            task=task
        )
        user_params["encoder_decoder"] = encdec_name

# Display current configuration
st.header("🔧 Current Configuration")
st.json(user_params)

# Run button
if st.button("🚀 Run Task", type="primary"):
    st.success("Your selections:")
    st.json(user_params)
