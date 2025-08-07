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
    encoder_df = pd.DataFrame(encoder_models)
    selected_encoder = aggrid_model_picker(encoder_df, key="aggrid_encoder_model_picker")
    if selected_encoder:
        st.success(f"Selected encoder: {selected_encoder['name']}")
        st.write(selected_encoder)

    st.subheader("Select a Decoder Model")
    decoder_df = pd.DataFrame(decoder_models)
    selected_decoder = aggrid_model_picker(decoder_df, key="aggrid_decoder_model_picker")
    if selected_decoder:
        st.success(f"Selected decoder: {selected_decoder['name']}")
        st.write(selected_decoder)

elif task in ("Normal QA", "Summarisation"):
    st.subheader("Select an Encoder-Decoder Model")
    encoder_decoder_df = pd.DataFrame(encoder_decoder_models)
    selected_encoder_decoder = aggrid_model_picker(encoder_decoder_df, key="aggrid_encoder_decoder_model_picker")
    if selected_encoder_decoder:
        st.success(f"Selected encoder-decoder: {selected_encoder_decoder['name']}")
        st.write(selected_encoder_decoder)

# --- Editable parameter tables with AgGrid
for block in get_task_param_blocks(task):
    param_type = f"{block}_parameters"
    params = get_task_parameters(task, param_type)
    if params:
        st.subheader(block.capitalize())
        # param_values = smart_param_table(params, key=f"param_{block}")
        param_values = smart_param_table_with_reset(params, title=block.capitalize())

        st.write(f"Values for {block}:", param_values)
