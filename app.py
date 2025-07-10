import streamlit as st
from typing import List
from components.encoder import LangchainEncoder
from components.decoder import LangchainDecoder
from components.encoder_decoder import EncoderDecoder
from vectorstore import VectorStoreBuilder
from langchain.chains import RetrievalQA
from transformers.pipelines import pipeline
import re
import gc
import yaml

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

# =====================
# Model options (loaded from models.yaml)
# =====================
def load_models():
    """Load model lists from models.yaml file."""
    with open('models.yaml', 'r') as file:
        models_data = yaml.safe_load(file)
    
    # Create the same variable names as before for compatibility
    SENTENCE_TRANSFORMER_ENCODERS = models_data['sentence_transformer_encoders']
    OTHER_ENCODERS = models_data['other_encoders']
    OTHER_DECODER_MODELS = models_data['other_decoder_models']
    QA_TUNED_MODELS = models_data['qa_tuned_models']
    OTHER_ENCODER_DECODER_MODELS = models_data['other_encoder_decoder_models']
    
    # Create derived lists
    ENCODER_ONLY_MODELS = SENTENCE_TRANSFORMER_ENCODERS + OTHER_ENCODERS
    DECODER_ONLY_MODELS = OTHER_DECODER_MODELS
    ENCODER_DECODER_MODELS = QA_TUNED_MODELS + OTHER_ENCODER_DECODER_MODELS
    
    return {
        'SENTENCE_TRANSFORMER_ENCODERS': SENTENCE_TRANSFORMER_ENCODERS,
        'OTHER_ENCODERS': OTHER_ENCODERS,
        'ENCODER_ONLY_MODELS': ENCODER_ONLY_MODELS,
        'OTHER_DECODER_MODELS': OTHER_DECODER_MODELS,
        'DECODER_ONLY_MODELS': DECODER_ONLY_MODELS,
        'QA_TUNED_MODELS': QA_TUNED_MODELS,
        'OTHER_ENCODER_DECODER_MODELS': OTHER_ENCODER_DECODER_MODELS,
        'ENCODER_DECODER_MODELS': ENCODER_DECODER_MODELS
    }

# Load models
models = load_models()

# Sidebar for task selection
st.sidebar.header("Task Selection")
task = st.sidebar.radio("Choose task:", ["Normal QA", "RAG-based QA", "Summarisation"])

# Common generation parameters
def generation_params():
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    top_k = st.slider("Top-K", 1, 50, 5)
    return temperature, top_k

def clean_model_name(model_name):
    """Remove text in parentheses and strip whitespace."""
    return re.sub(r"\s*\([^)]*\)", "", model_name).strip()

def free_memory():
    """Frees up CPU and GPU memory after each submission."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    except ImportError:
        pass

if task == "RAG-based QA":
    st.header("RAG-based Question Answering")
    uploaded_file = st.file_uploader("Upload document", type=["txt", "pdf"])
    encoder_model = st.selectbox("Choose encoder model:", models['SENTENCE_TRANSFORMER_ENCODERS'])
    decoder_model = st.selectbox("Choose decoder model:", models['OTHER_DECODER_MODELS'])
    temperature, top_k = generation_params()
    max_length = st.number_input("Max Length", min_value=1, max_value=2048, value=128)
    top_p = st.slider("Top-p (nucleus sampling)", 0.0, 1.0, 1.0)
    st.info("""
    **Hints:**
    - High temperature makes the model output more random and creative, but less reliable.
    - High top_k allows sampling from a larger pool of possible next words, increasing diversity but possibly reducing coherence.
    - Lower top_p focuses generation on the most likely words.
    """)
    custom_prompt = st.text_area("Optional prompt:", "Answer based on the context:")
    query = st.text_input("Enter your question:")

    if uploaded_file and query:
        if uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            document = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        else:
            document = uploaded_file.read().decode("utf-8")
        docs = document.split("\n")

        encoder = LangchainEncoder(clean_model_name(encoder_model))
        vs_builder = VectorStoreBuilder(clean_model_name(encoder_model))
        retriever = vs_builder.get_retriever(docs, top_k)
        decoder = LangchainDecoder(
            clean_model_name(decoder_model),
            temperature=temperature,
            max_length=max_length,
            top_k=top_k,
            top_p=top_p
        )
        llm = decoder.get_llm()
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")
        final_prompt = f"{custom_prompt}\nQuestion: {query}"
        result = qa_chain.run(final_prompt)
        st.markdown("### 🧾 Answer")
        st.write(result)
        del encoder, vs_builder, retriever, decoder, llm, qa_chain
        free_memory()

elif task == "Normal QA":
    st.header("Normal Abstractive Question Answering")
    # Combine QA-tuned and encoder-decoder models for selection
    encoder_decoder_model = st.selectbox("Choose QA model:", models['QA_TUNED_MODELS'])
    temperature, top_k = generation_params()
    st.info("""
    **Hints:**
    - High temperature makes the model output more random and creative, but less reliable.
    - High top_k allows sampling from a larger pool of possible next words, increasing diversity but possibly reducing coherence.
    """)
    query = st.text_input("Ask a question:")
    model_id = clean_model_name(encoder_decoder_model).lower()
    qa_model = EncoderDecoder(model_name=model_id, task="text2text-generation", temperature=temperature)
    response = qa_model.run(query)
    del qa_model
    st.markdown("### 💬 Answer")
    st.write(response)
    free_memory()

elif task == "Summarisation":
    st.header("Summarisation Task")
    uploaded_file = st.file_uploader("Upload document for summarization", type=["txt", "pdf"])
    decoder_model = st.selectbox("Choose summarization model:", models['ENCODER_DECODER_MODELS'])
    temperature, _ = generation_params()
    st.info("""
    **Hints:**
    - High temperature makes the summary more creative and less deterministic.
    - High top_k increases diversity but may reduce focus and coherence.
    """)
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        else:
            text = uploaded_file.read().decode("utf-8")
        summarizer = EncoderDecoder(model_name=clean_model_name(decoder_model), task="summarization", temperature=temperature)
        summary = summarizer.run(text[:1024])
        st.markdown("### 📄 Summary")
        st.write(summary)
        del summarizer
        free_memory()