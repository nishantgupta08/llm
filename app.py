import streamlit as st
import json
import pandas as pd
import os

from core.task_config import (
    get_available_tasks, get_task_param_blocks, get_task_parameters,
    get_task_description, get_task_icon
)
from utils.ui import aggrid_model_picker, create_preprocessing_table, create_encoding_table, create_decoding_table

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

# --- Sidebar with task selection ---
with st.sidebar:
    st.markdown("## 🎯 Task Selection")
    tasks = get_available_tasks()
    task = st.selectbox("Choose Task", tasks)

# --- Main content area ---
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

    # --- Query input and PDF upload ---
    from utils.ui.display import query_input_box, pdf_upload_widget
    st.markdown("---")
    st.subheader("User Query and Document Upload")
    user_query = query_input_box()
    uploaded_pdf = pdf_upload_widget()

    # --- Run button ---
    run_clicked = st.button("Run RAG QA")
    if run_clicked:
        if not (selected_encoder and selected_decoder):
            st.error("Please select both an encoder and a decoder model.")
        elif not user_query:
            st.error("Please enter a query.")
        elif not uploaded_pdf:
            st.error("Please upload a PDF document.")
        else:
            with st.spinner("Running RAG-based QA..."):
                from core.task_orchestrator import TaskOrchestrator
                orchestrator = TaskOrchestrator(models_json)
                answer = orchestrator.run_rag_qa(
                    file=uploaded_pdf,
                    encoder_name=selected_encoder['name'],
                    decoder_name=selected_decoder['name'],
                    prompt="",  # You may want to add a prompt input
                    query=user_query,
                    encoding_params=None,
                    decoding_params=None,
                    preprocessing_config=None
                )
                st.success("Answer:")
                st.write(answer)

elif task in ("Normal QA", "Summarisation"):
    st.subheader("Select an Encoder-Decoder Model")
    encoder_decoder_df = pd.DataFrame(encoder_decoder_models)
    selected_encoder_decoder = aggrid_model_picker(encoder_decoder_df, key="aggrid_encoder_decoder_model_picker")
    if selected_encoder_decoder:
        st.success(f"Selected encoder-decoder: {selected_encoder_decoder['name']}")
        st.write(selected_encoder_decoder)

# --- Parameter configuration section ---
st.markdown("---")
st.markdown("## ⚙️ Parameter Configuration")

# --- Parameter configuration tabs ---
param_blocks = get_task_param_blocks(task)
if param_blocks:
    tab_names = []
    for block in param_blocks:
        if block.lower() == "encoding":
            tab_names.append("🔧 Encoding")
        elif block.lower() == "decoding":
            tab_names.append("🎲 Decoding")
        elif block.lower() == "preprocessing":
            tab_names.append("📝 Preprocessing")
    
    if tab_names:
        tabs = st.tabs(tab_names)
        
        for i, block in enumerate(param_blocks):
            param_type = f"{block}_parameters"
            params = get_task_parameters(task, param_type)
            
            if params:
                with tabs[i]:
                    if block.lower() == "encoding":
                        create_encoding_table(params, task)
                    elif block.lower() == "decoding":
                        create_decoding_table(params, task)
                    elif block.lower() == "preprocessing":
                        create_preprocessing_table(params, task)
