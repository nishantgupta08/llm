import streamlit as st
import json
import pandas as pd
from config.task_config import (
    get_available_tasks, get_task_parameters, get_ideal_value, get_ideal_value_reason,
    get_task_param_blocks, get_task_description, get_task_icon, get_task_config
)
from utils.ui_utils import parameter_table, model_picker_table

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

tasks = get_available_tasks()
task_choice = st.sidebar.selectbox("Choose Task", tasks)

st.markdown(f"### {get_task_icon(task_choice)} {task_choice}")
st.write(get_task_description(task_choice))

# Load models from JSON
with open("config/models.json") as f:
    models_json = json.load(f)

all_models = (
    models_json.get("ENCODER_ONLY_MODELS", []) +
    models_json.get("DECODER_ONLY_MODELS", []) +
    models_json.get("ENCODER_DECODER_MODELS", [])
)
models_df = pd.DataFrame(all_models)

# Get task config to see which model selectors are needed
task_cfg = get_task_config(task_choice)
model_blocks = [b for b in ("encoder", "decoder", "encoder_decoder") if task_cfg.get("ui_blocks", []) and b in task_cfg["ui_blocks"]]

# Model selection section (uses the interactive picker table)
if model_blocks:
    st.subheader("Select a Model")
    selected_model = model_picker_table(models_df)
    if selected_model is not None:
        st.success(f"**You selected model:** {selected_model['name']}")
        st.table(selected_model)

# Show parameter tables
for block in get_task_param_blocks(task_choice):
    param_type = f"{block}_parameters"
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
