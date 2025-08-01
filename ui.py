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
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from strategies.types import InputType, ValueType
from utils.ui_helper import decoding_param_widgets, model_dropdown, encoding_param_widgets, model_table_selection, preprocessing_param_widgets, display_parameters_table, display_compact_widgets_table
import pandas as pd

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

# Use the new model config
models = {
    "ENCODER_ONLY_MODELS": ENCODER_ONLY_MODELS,
    "DECODER_ONLY_MODELS": DECODER_ONLY_MODELS,
    "ENCODER_DECODER_MODELS": ENCODER_DECODER_MODELS,
}

orchestrator = TaskOrchestrator(models)

# Create two-column layout
col_left, col_right = st.columns([1, 3])

# Left side - Task selection and model statistics
with col_left:
    st.header("🎯 Task Selection")
    task = st.radio("Choose task:", ["Normal QA", "RAG-based QA", "Summarisation"])
    
    # Model statistics
    with st.expander("📊 Model Statistics", expanded=False):
        st.write(f"🔍 Model Counts:")
        st.write(f"  - Encoder models: {len(ENCODER_ONLY_MODELS)}")
        st.write(f"  - Decoder models: {len(DECODER_ONLY_MODELS)}")
        st.write(f"  - Encoder-Decoder models: {len(ENCODER_DECODER_MODELS)}")

# Right side - Main content
with col_right:
    # Demo section to showcase different table widget approaches
    with st.expander("🎨 Table Widget Demo", expanded=False):
        st.markdown("### Different approaches to show widgets in tables:")
        
        # Demo parameters
        demo_params = [
            {"name": "temperature", "label": "Temperature", "type": "slider", "value": 0.7, "range": "0.0-1.5"},
            {"name": "top_k", "label": "Top-K", "type": "number", "value": 50, "range": "0-100"},
            {"name": "pooling", "label": "Pooling", "type": "dropdown", "value": "mean", "options": ["mean", "max", "cls"]},
            {"name": "normalize", "label": "Normalize", "type": "checkbox", "value": True}
        ]
        
        tab1, tab2, tab3 = st.tabs(["📊 Regular Table", "🎛️ Compact Widgets", "🔧 Interactive Grid"])
        
        with tab1:
            st.markdown("**Traditional approach:** Table + widgets below")
            # Create a simple table
            df = pd.DataFrame(demo_params)
            st.dataframe(df[["label", "type", "value", "range"]], use_container_width=True)
            
            # Widgets below table
            st.markdown("**Controls:**")
            for param in demo_params:
                if param["type"] == "slider":
                    st.slider(param["label"], 0.0, 2.0, param["value"], 0.1)
                elif param["type"] == "number":
                    st.number_input(param["label"], 0, 100, param["value"])
                elif param["type"] == "dropdown":
                    st.selectbox(param["label"], param["options"], index=0)
                elif param["type"] == "checkbox":
                    st.checkbox(param["label"], param["value"])
        
        with tab2:
            st.markdown("**Compact approach:** Widgets inline with table layout")
            # Create table header
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            with col1:
                st.markdown("**Parameter**")
            with col2:
                st.markdown("**Type**")
            with col3:
                st.markdown("**Range**")
            with col4:
                st.markdown("**Control**")
            
            st.divider()
            
            # Create rows with widgets
            for param in demo_params:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                with col1:
                    st.markdown(f"**{param['label']}**")
                with col2:
                    st.markdown(f"`{param['type']}`")
                with col3:
                    st.markdown(f"`{param['range']}`")
                with col4:
                    if param["type"] == "slider":
                        st.slider("Value", 0.0, 2.0, param["value"], 0.1, label_visibility="collapsed")
                    elif param["type"] == "number":
                        st.number_input("Value", 0, 100, param["value"], label_visibility="collapsed")
                    elif param["type"] == "dropdown":
                        st.selectbox("Value", param["options"], index=0, label_visibility="collapsed")
                    elif param["type"] == "checkbox":
                        st.checkbox("Value", param["value"], label_visibility="collapsed")
                st.divider()
        
        with tab3:
            st.markdown("**Advanced approach:** Interactive grid with embedded controls")
            st.info("This would use st_aggrid with custom cell renderers for widgets")
            st.caption("💡 Requires advanced JavaScript integration")

    if task == "RAG-based QA":
        st.header("\U0001F50D RAG-based Question Answering")
        
        # 1. File upload
        with st.expander("📁 Document Upload", expanded=True):
            file = st.file_uploader("Upload document", type=["pdf", "txt"])
            if file:
                st.success(f"✅ File uploaded: {file.name}")
        
        # 2. Optional prompt
        with st.expander("📝 Optional Prompt", expanded=True):
            prompt = st.text_area("Prompt", "Answer based on the context:")
        
        # 3. Query
        with st.expander("❓ Query", expanded=True):
            query = st.text_input("Ask a question")
        
        # 4. Preprocessing parameters
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        if preprocessing_params_list:
            with st.expander("⚙️ Preprocessing Parameters", expanded=False):
                preprocessing_params = display_compact_widgets_table(preprocessing_params_list, "Preprocessing Parameters", sidebar=False)
        
        # 5. Encoding parameters
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        if encoding_params_list:
            with st.expander("🔧 Encoding Parameters", expanded=False):
                encoding_params = display_compact_widgets_table(encoding_params_list, "Encoding Parameters", sidebar=False)
        
        # 6. Decoding parameters
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        if decoding_params_list:
            with st.expander("🎯 Decoding Parameters", expanded=False):
                decoding_params = display_compact_widgets_table(decoding_params_list, "Decoding Parameters", sidebar=False)
        
        # Model selection
        with st.expander("🤖 Model Selection", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                encoder = model_table_selection("Encoder Model", ENCODER_ONLY_MODELS, task, prefix="encoder")
            with col2:
                decoder = model_table_selection("Decoder Model", DECODER_ONLY_MODELS, task, prefix="decoder")
        
        # Submit button
        submit_rag = st.button("🚀 Run RAG Pipeline", type="primary")

        if submit_rag and file and query and encoder and decoder:
            with st.spinner("Running RAG pipeline..."):
                try:
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
        
        # 3. Query
        with st.expander("❓ Query", expanded=True):
            query = st.text_input("Ask a question")
        
        # 4. Preprocessing parameters
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        if preprocessing_params_list:
            with st.expander("⚙️ Preprocessing Parameters", expanded=False):
                preprocessing_params = display_compact_widgets_table(preprocessing_params_list, "Preprocessing Parameters", sidebar=False)
        
        # 5. Encoding parameters
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        if encoding_params_list:
            with st.expander("🔧 Encoding Parameters", expanded=False):
                encoding_params = display_compact_widgets_table(encoding_params_list, "Encoding Parameters", sidebar=False)
        
        # 6. Decoding parameters
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        if decoding_params_list:
            with st.expander("🎯 Decoding Parameters", expanded=False):
                decoding_params = display_compact_widgets_table(decoding_params_list, "Decoding Parameters", sidebar=False)
        
        # Model selection
        with st.expander("🤖 Model Selection", expanded=True):
            model = model_table_selection("QA Model", ENCODER_DECODER_MODELS, task, prefix="qa")
        
        # Submit button
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
        
        # 1. File upload
        with st.expander("📁 Document Upload", expanded=True):
            file = st.file_uploader("Upload document", type=["pdf", "txt"])
            if file:
                st.success(f"✅ File uploaded: {file.name}")
        
        # 4. Preprocessing parameters
        preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
        if preprocessing_params_list:
            with st.expander("⚙️ Preprocessing Parameters", expanded=False):
                preprocessing_params = display_compact_widgets_table(preprocessing_params_list, "Preprocessing Parameters", sidebar=False)
        
        # 5. Encoding parameters
        encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
        if encoding_params_list:
            with st.expander("🔧 Encoding Parameters", expanded=False):
                encoding_params = display_compact_widgets_table(encoding_params_list, "Encoding Parameters", sidebar=False)
        
        # 6. Decoding parameters
        decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
        if decoding_params_list:
            with st.expander("🎯 Decoding Parameters", expanded=False):
                decoding_params = display_compact_widgets_table(decoding_params_list, "Decoding Parameters", sidebar=False)
        
        # Model selection
        with st.expander("🤖 Model Selection", expanded=True):
            model = model_table_selection("Summarisation Model", ENCODER_DECODER_MODELS, task, prefix="summary")
        
        # Submit button
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
