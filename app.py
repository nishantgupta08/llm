import streamlit as st
from config.tasks import (
    get_available_tasks, get_task_parameters, get_ideal_value, get_ideal_value_reason,
    get_task_param_blocks, get_task_description, get_task_icon, get_task_config
)
from config.models import ENCODER_ONLY_MODELS, DECODER_ONLY_MODELS, ENCODER_DECODER_MODELS
from utils.ui_utils import parameter_table, model_dropdown

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

tasks = get_available_tasks()
task_choice = st.sidebar.selectbox("Choose Task", tasks)

st.markdown(f"### {get_task_icon(task_choice)} {task_choice}")
st.write(get_task_description(task_choice))

# Get task config to see which model selectors are needed
task_cfg = get_task_config(task_choice)
model_blocks = [b for b in ("encoder", "decoder", "encoder_decoder") if task_cfg.get("ui_blocks", []) and b in task_cfg["ui_blocks"]]

# Show model selector(s) if required
for block in model_blocks:
    if block == "encoder":
        st.subheader("Encoder Model")
        model = model_dropdown("Select Encoder Model", ENCODER_ONLY_MODELS)
        st.write("Selected encoder model:", model)
    elif block == "decoder":
        st.subheader("Decoder Model")
        model = model_dropdown("Select Decoder Model", DECODER_ONLY_MODELS)
        st.write("Selected decoder model:", model)
    elif block == "encoder_decoder":
        st.subheader("Encoder-Decoder Model")
        model = model_dropdown("Select Encoder-Decoder Model", ENCODER_DECODER_MODELS)
        st.write("Selected encoder-decoder model:", model)

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
