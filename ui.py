import streamlit as st
from task_config import (
    get_available_tasks,
    get_task_ui_config,
    get_task_description,
    get_task_icon,
    has_ui_block,
    has_param_block
)
from models_config import (
    ENCODER_ONLY_MODELS,
    DECODER_ONLY_MODELS,
    ENCODER_DECODER_MODELS
)
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from strategies.encoding_strategies import TASK_ENCODING_PARAMS
from strategies.decoding_strategies import TASK_DECODING_PARAMS
from utils.ui_helper import display_compact_widgets_table, model_dropdown

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

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
col1, col2 = st.columns([1, 3])

with col1:
    st.header("📋 Configuration")
    
    # Parameter Tables
    if has_param_block(task, "preprocessing"):
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        if preprocessing_params_list:
            user_params["preprocessing"] = display_compact_widgets_table(
                preprocessing_params_list, 
                title="Preprocessing Parameters",
                sidebar=False
            )

    if has_param_block(task, "encoding"):
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        if encoding_params_list:
            user_params["encoding"] = display_compact_widgets_table(
                encoding_params_list, 
                title="Encoding Parameters",
                sidebar=False
            )

    if has_param_block(task, "decoding"):
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        if decoding_params_list:
            user_params["decoding"] = display_compact_widgets_table(
                decoding_params_list, 
                title="Decoding Parameters",
                sidebar=False
            )

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

# Run button
if st.button("🚀 Run Task", type="primary"):
    st.success("Your selections:")
    st.json(user_params)
