import streamlit as st
import json
import pandas as pd
from config.core import get_tasks, get_task_blocks, get_parameters, get_task_description, get_task_icon
from utils.ui_utils import parameter_table, model_picker_table

# --- Load Config ---
with open("config/models.json") as f:
    models = pd.DataFrame(
        sum((models for models in json.load(f).values()), [])
    )

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

task = st.sidebar.selectbox("Choose Task", get_tasks())
st.markdown(f"### {get_task_icon(task)} {task}")
st.write(get_task_description(task))

# --- Model Selection ---
st.subheader("Select a Model")
selected_model = model_picker_table(models)
if selected_model is not None:
    st.success(f"**You selected:** {selected_model['name']}")
    st.table(selected_model)

# --- Parameter Tables ---
for block in get_task_blocks(task):
    params = get_parameters(task, block)
    if params:
        st.subheader(block.capitalize())
        st.write(parameter_table(params, task, block))
