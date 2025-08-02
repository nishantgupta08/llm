import streamlit as st
from config.tasks import (
    get_available_tasks,
    get_task_parameters,
    get_ideal_value,
    get_ideal_value_reason,
    get_task_param_blocks,
    get_task_description,
    get_task_icon
)
from utils.ui_utils import parameter_table

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

# Task selection
tasks = get_available_tasks()
task_choice = st.sidebar.selectbox("Choose Task", tasks)

st.markdown(f"### {get_task_icon(task_choice)} {task_choice}")
st.write(get_task_description(task_choice))

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
