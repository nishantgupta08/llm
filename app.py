import streamlit as st
import pandas as pd
from core.task_config import (
    get_available_tasks,
    get_task_parameters,
    get_ideal_value,
    get_ideal_value_reason,
    get_task_param_blocks,
    get_task_description,
    get_task_icon,
    get_task_ui_blocks,
    ENCODER_ONLY_MODELS,
    DECODER_ONLY_MODELS,
    ENCODER_DECODER_MODELS
)
from utils.ui_utils import parameter_table, model_picker_table_with_checkboxes

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

# Task selection
tasks = get_available_tasks()
task_choice = st.sidebar.selectbox("Choose Task", tasks)

st.markdown(f"### {get_task_icon(task_choice)} {task_choice}")
st.write(get_task_description(task_choice))

# Get UI blocks for the selected task
ui_blocks = get_task_ui_blocks(task_choice)

# Model Selection Section
st.markdown("### 🤖 Model Selection")

# Create model selection tables based on UI blocks
selected_models = {}

if "encoder" in ui_blocks:
    st.markdown("#### Encoder Models")
    encoder_df = pd.DataFrame(ENCODER_ONLY_MODELS)
    if not encoder_df.empty:
        selected_encoder = model_picker_table_with_checkboxes(encoder_df, key="encoder_models")
        if selected_encoder is not None:
            selected_models["encoder"] = selected_encoder
            st.success(f"✅ Selected Encoder: {selected_encoder['name']}")
        else:
            st.info("ℹ️ Please select an encoder model from the table above.")
    else:
        st.warning("No encoder models available.")

if "decoder" in ui_blocks:
    st.markdown("#### Decoder Models")
    decoder_df = pd.DataFrame(DECODER_ONLY_MODELS)
    if not decoder_df.empty:
        selected_decoder = model_picker_table_with_checkboxes(decoder_df, key="decoder_models")
        if selected_decoder is not None:
            selected_models["decoder"] = selected_decoder
            st.success(f"✅ Selected Decoder: {selected_decoder['name']}")
        else:
            st.info("ℹ️ Please select a decoder model from the table above.")
    else:
        st.warning("No decoder models available.")

if "encoder_decoder" in ui_blocks:
    st.markdown("#### Encoder-Decoder Models")
    encoder_decoder_df = pd.DataFrame(ENCODER_DECODER_MODELS)
    if not encoder_decoder_df.empty:
        selected_encoder_decoder = model_picker_table_with_checkboxes(encoder_decoder_df, key="encoder_decoder_models")
        if selected_encoder_decoder is not None:
            selected_models["encoder_decoder"] = selected_encoder_decoder
            st.success(f"✅ Selected Encoder-Decoder: {selected_encoder_decoder['name']}")
        else:
            st.info("ℹ️ Please select an encoder-decoder model from the table above.")
    else:
        st.warning("No encoder-decoder models available.")

# Parameter Configuration Section
st.markdown("### ⚙️ Parameter Configuration")

# Loop through parameter blocks for the task (e.g., preprocessing, encoding, decoding)
for block in get_task_param_blocks(task_choice):
    # Map block to correct config section name, if needed
    param_type = f"{block}_parameters"  # e.g., 'encoding_parameters'
    params = get_task_parameters(task_choice, param_type)
    if params:
        st.subheader(block.capitalize())
        param_values = parameter_table(
            param_dict=params,
            task_name=task_choice,
            param_category=param_type,
            get_ideal_value=get_ideal_value,
            get_ideal_value_reason=get_ideal_value_reason
        )
        st.write(f"Values for {block}:", param_values)

# Display selected models summary
if selected_models:
    st.markdown("### 📋 Selected Models Summary")
    for model_type, model in selected_models.items():
        st.write(f"**{model_type.title()}**: {model['name']} ({model['type']}) - {model['size']}")
else:
    st.info("ℹ️ No models selected. Please select models from the tables above.")
