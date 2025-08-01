"""
ui.py

Streamlit UI for GenAI Playground: supports RAG-based QA, Normal QA, and Summarisation tasks.
"""

import streamlit as st
from models_config import ENCODER_ONLY_MODELS, DECODER_ONLY_MODELS, ENCODER_DECODER_MODELS, ModelInfo
from utils.helper import (
    free_memory,
    get_text_from_file
    )
from core.task_orchestrator import TaskOrchestrator
from strategies.decoding_strategies import TASK_DECODING_PARAMS
from strategies.encoding_strategies import TASK_ENCODING_PARAMS, EncodingParam
from strategies.types import InputType, ValueType
from utils.ui_helper import decoding_param_widgets, model_dropdown, encoding_param_widgets, model_table_selection, preprocessing_param_widgets, display_parameters_table

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

# Use the new model config
models = {
    "ENCODER_ONLY_MODELS": ENCODER_ONLY_MODELS,
    "DECODER_ONLY_MODELS": DECODER_ONLY_MODELS,
    "ENCODER_DECODER_MODELS": ENCODER_DECODER_MODELS,
}

# Debug: Show model counts in an expander
with st.sidebar.expander("📊 Model Statistics", expanded=False):
    st.write(f"🔍 Model Counts:")
    st.write(f"  - Encoder models: {len(ENCODER_ONLY_MODELS)}")
    st.write(f"  - Decoder models: {len(DECODER_ONLY_MODELS)}")
    st.write(f"  - Encoder-Decoder models: {len(ENCODER_DECODER_MODELS)}")

orchestrator = TaskOrchestrator(models)

# Task selection
st.sidebar.header("🎯 Task Selection")
task = st.sidebar.radio("Choose task:", ["Normal QA", "RAG-based QA", "Summarisation"])

if task == "RAG-based QA":
    st.header("\U0001F50D RAG-based Question Answering")
    
    # File upload section
    with st.expander("📁 Document Upload", expanded=True):
        file = st.file_uploader("Upload document", type=["pdf", "txt"])
        if file:
            st.success(f"✅ File uploaded: {file.name}")
    
    # Model selection section
    with st.expander("🤖 Model Selection", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            encoder = model_table_selection("Encoder Model", ENCODER_ONLY_MODELS, task, prefix="encoder")
        
        with col2:
            decoder = model_table_selection("Decoder Model", DECODER_ONLY_MODELS, task, prefix="decoder")
    
    # Configuration section
    with st.expander("⚙️ Advanced Configuration", expanded=False):
        st.info("💡 Configure model behavior with these parameter groups:")
        
        # Get parameter lists
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        
        # Display parameters in tabular format
        col1, col2 = st.columns(2)
        
        with col1:
            encoding_params = display_parameters_table(encoding_params_list, "Encoding Parameters", sidebar=False)
            decoding_params = display_parameters_table(decoding_params_list, "Decoding Parameters", sidebar=False)
        
        with col2:
            preprocessing_params = display_parameters_table(preprocessing_params_list, "Preprocessing Parameters", sidebar=False)
    
    # Query section
    with st.expander("❓ Query & Prompt", expanded=True):
        prompt = st.text_area("Optional Prompt", "Answer based on the context:")
        query = st.text_input("Ask a question")
    
    # Add submit button
    submit_rag = st.button("🚀 Run RAG Pipeline", type="primary")

    if submit_rag and file and query and encoder and decoder:
        with st.spinner("Running RAG pipeline..."):
            try:
                # Pass preprocessing parameters
                result = orchestrator.run_rag_qa(
                    file, encoder, decoder, prompt, query,
                    encoding_params=encoding_params,
                    decoding_params=decoding_params,
                    preprocessing_config=preprocessing_params
                )
                st.success("Answer ready:")
                st.write(result)
            except Exception as e:
                st.error(str(e))
            finally:
                free_memory()
    elif submit_rag and (not file or not query or not encoder or not decoder):
        st.warning("Please upload a document, enter a question, and select both encoder and decoder models.")

elif task == "Normal QA":
    st.header("\U0001F4AC Normal Question Answering")
    
    # Model selection section
    with st.expander("🤖 Model Selection", expanded=True):
        model = model_table_selection("QA Model", ENCODER_DECODER_MODELS, task, prefix="qa")
    
    # Configuration section
    with st.expander("⚙️ Advanced Configuration", expanded=False):
        st.info("💡 Configure model behavior with these parameter groups:")
        
        # Get parameter lists
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        
        # Display parameters in tabular format
        col1, col2 = st.columns(2)
        
        with col1:
            encoding_params = display_parameters_table(encoding_params_list, "Encoding Parameters", sidebar=False)
            decoding_params = display_parameters_table(decoding_params_list, "Decoding Parameters", sidebar=False)
        
        with col2:
            preprocessing_params = display_parameters_table(preprocessing_params_list, "Preprocessing Parameters", sidebar=False)
    
    # Query section
    with st.expander("❓ Query", expanded=True):
        query = st.text_input("Ask a question")
    
    # Add submit button
    submit_qa = st.button("🚀 Generate Answer", type="primary")

    if submit_qa and query and model:
        with st.spinner("Generating answer..."):
            try:
                result = orchestrator.run_qa(model, query, encoding_params=encoding_params,
                    decoding_params=decoding_params, preprocessing_config=preprocessing_params)
                st.success("Answer ready:")
                st.write(result)
            except Exception as e:
                st.error(str(e))
            finally:
                free_memory()
    elif submit_qa and (not query or not model):
        st.warning("Please enter a question and select a model.")

elif task == "Summarisation":
    st.header("📄 Summarisation Task")
    
    # File upload section
    with st.expander("📁 Document Upload", expanded=True):
        file = st.file_uploader("Upload document", type=["pdf", "txt"])
        if file:
            st.success(f"✅ File uploaded: {file.name}")
    
    # Model selection section
    with st.expander("🤖 Model Selection", expanded=True):
        model = model_table_selection("Summarisation Model", ENCODER_DECODER_MODELS, task, prefix="summary")
    
    # Configuration section
    with st.expander("⚙️ Advanced Configuration", expanded=False):
        st.info("💡 Configure model behavior with these parameter groups:")
        
        # Get parameter lists
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        
        # Display parameters in tabular format
        col1, col2 = st.columns(2)
        
        with col1:
            encoding_params = display_parameters_table(encoding_params_list, "Encoding Parameters", sidebar=False)
            decoding_params = display_parameters_table(decoding_params_list, "Decoding Parameters", sidebar=False)
        
        with col2:
            preprocessing_params = display_parameters_table(preprocessing_params_list, "Preprocessing Parameters", sidebar=False)
    
    # Add submit button
    submit_summary = st.button("🚀 Generate Summary", type="primary")

    if submit_summary and file and model:
        with st.spinner("Summarizing text..."):
            try:
                text = get_text_from_file(file, max_chars=1024)
                
                result = orchestrator.run_summarisation(model, text, encoding_params=encoding_params,
                    decoding_params=decoding_params, preprocessing_config=preprocessing_params)
                st.success("Summary ready:")
                st.write(result)
            except Exception as e:
                st.error(str(e))
            finally:
                free_memory()
    elif submit_summary and (not file or not model):
        st.warning("Please upload a document and select a model.")
