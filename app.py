import streamlit as st
import json
import pandas as pd
import os

from core.task_config import (
    get_available_tasks, get_task_param_blocks, get_task_parameters,
    get_task_description, get_task_icon
)
from utils.ui_utils import aggrid_model_picker, smart_param_table_with_reset

# --- Load models from JSON
config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
with open(os.path.join(config_dir, "models.json")) as f:
    models_json = json.load(f)
all_models = (
    models_json.get("ENCODER_ONLY_MODELS", []) +
    models_json.get("DECODER_ONLY_MODELS", []) +
    models_json.get("ENCODER_DECODER_MODELS", [])
)
models_df = pd.DataFrame(all_models)

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

tasks = get_available_tasks()
task = st.sidebar.selectbox("Choose Task", tasks)
st.markdown(f"### {get_task_icon(task)} {task}")
st.write(get_task_description(task))

# --- Model selection widgets based on task ---
encoder_models = [m for m in models_json.get('ENCODER_ONLY_MODELS', [])]
decoder_models = [m for m in models_json.get('DECODER_ONLY_MODELS', [])]
encoder_decoder_models = [m for m in models_json.get('ENCODER_DECODER_MODELS', [])]

selected_encoder = selected_decoder = selected_encoder_decoder = None

if task == "RAG-based QA":
    st.subheader("Select an Encoder Model")
    selected_encoder = st.selectbox(
        "Encoder Model", [m['name'] for m in encoder_models], key="encoder_model_select"
    )
    st.subheader("Select a Decoder Model")
    selected_decoder = st.selectbox(
        "Decoder Model", [m['name'] for m in decoder_models], key="decoder_model_select"
    )
elif task in ("Normal QA", "Summarisation"):
    st.subheader("Select an Encoder-Decoder Model")
    selected_encoder_decoder = st.selectbox(
        "Encoder-Decoder Model", [m['name'] for m in encoder_decoder_models], key="encoder_decoder_model_select"
    )

# --- Model selection with AgGrid
st.subheader("Select a Model")
selected_model = aggrid_model_picker(models_df)
if selected_model is not None:
    st.success(f"**Selected model:** {selected_model['name']}")
    st.write(selected_model)

    # --- Show relevant selection options based on model type ---
    encoder_names = [m['name'] for m in models_json.get('ENCODER_ONLY_MODELS', [])]
    decoder_names = [m['name'] for m in models_json.get('DECODER_ONLY_MODELS', [])]
    encoder_decoder_names = [m['name'] for m in models_json.get('ENCODER_DECODER_MODELS', [])]

    if selected_model['name'] in encoder_names:
        st.info('You have selected an **Encoder** model. Configure encoder options below.')
        # Place encoder-specific options here if needed
    elif selected_model['name'] in decoder_names:
        st.info('You have selected a **Decoder** model. Configure decoder options below.')
        # Place decoder-specific options here if needed
    elif selected_model['name'] in encoder_decoder_names:
        st.info('You have selected an **Encoder-Decoder** model. Configure encoder-decoder options below.')
        # Place encoder-decoder-specific options here if needed
    else:
        st.warning('Unknown model type.')
else:
    st.info("Please select a model from the table above.")

# --- Editable parameter tables with AgGrid
for block in get_task_param_blocks(task):
    param_type = f"{block}_parameters"
    params = get_task_parameters(task, param_type)
    if params:
        st.subheader(block.capitalize())
        # param_values = smart_param_table(params, key=f"param_{block}")
        param_values = smart_param_table_with_reset(params, title=block.capitalize())

        st.write(f"Values for {block}:", param_values)
