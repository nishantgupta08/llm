import streamlit as st
import json
import pandas as pd
import os

from core.task_config import (
    get_available_tasks, get_task_param_blocks, get_task_parameters,
    get_task_description, get_task_icon
)
from utils.ui_utils import aggrid_model_picker, smart_param_table

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

# --- Model selection with AgGrid
st.subheader("Select a Model")
selected_model = aggrid_model_picker(models_df)
if selected_model is not None:
    st.success(f"**Selected model:** {selected_model['name']}")
    st.write(selected_model)
else:
    st.info("Please select a model from the table above.")

# --- Editable parameter tables with AgGrid
for block in get_task_param_blocks(task):
    param_type = f"{block}_parameters"
    params = get_task_parameters(task, param_type)
    if params:
        st.subheader(block.capitalize())
        param_values = smart_param_table(params, key=f"param_{block}")
        st.write(f"Values for {block}:", param_values)
