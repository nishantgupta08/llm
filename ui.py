import streamlit as st
from models_config import (
    ENCODER_ONLY_MODELS,
    DECODER_ONLY_MODELS,
    ENCODER_DECODER_MODELS
)
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from strategies.encoding_strategies import TASK_ENCODING_PARAMS
from strategies.decoding_strategies import TASK_DECODING_PARAMS
from utils.ui_helper import render_param_table, model_table_selection

# Task configuration
TASK_CONFIG = {
    "RAG-based QA": {
        "preprocessing": True,
        "encoding": True,
        "decoding": False,
        "encoder": True,
        "decoder": False,
        "encoder_decoder": False,
    },
    "Normal QA": {
        "preprocessing": True,
        "encoding": True,
        "decoding": True,
        "encoder": False,
        "decoder": False,
        "encoder_decoder": True,
    },
    "Summarisation": {
        "preprocessing": True,
        "encoding": True,
        "decoding": True,
        "encoder": False,
        "decoder": False,
        "encoder_decoder": True,
    }
}

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

task = st.radio("Choose task:", list(TASK_CONFIG.keys()))
cfg = TASK_CONFIG[task]
user_params = {}

# Preprocessing Parameters Table
if cfg.get("preprocessing"):
    preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
    if preprocessing_params_list:
        user_params["preprocessing"] = render_param_table(preprocessing_params_list, title="Preprocessing Parameters")

# Encoding Parameters Table
if cfg.get("encoding"):
    encoding_params_list = TASK_ENCODING_PARAMS.get(task, [])
    if encoding_params_list:
        user_params["encoding"] = render_param_table(encoding_params_list, title="Encoding Parameters")

# Decoding Parameters Table
if cfg.get("decoding"):
    decoding_params_list = TASK_DECODING_PARAMS.get(task, [])
    if decoding_params_list:
        user_params["decoding"] = render_param_table(decoding_params_list, title="Decoding Parameters")

# Model selection sections
if cfg.get("encoder"):
    encoder_obj = model_table_selection("Encoder Model", ENCODER_ONLY_MODELS, prefix="encoder")
    user_params["encoder"] = encoder_obj.name if encoder_obj else None

if cfg.get("decoder"):
    decoder_obj = model_table_selection("Decoder Model", DECODER_ONLY_MODELS, prefix="decoder")
    user_params["decoder"] = decoder_obj.name if decoder_obj else None

if cfg.get("encoder_decoder"):
    encdec_obj = model_table_selection("Encoder-Decoder Model", ENCODER_DECODER_MODELS, prefix="encdec")
    user_params["encoder_decoder"] = encdec_obj.name if encdec_obj else None

if st.button("🚀 Run Task", type="primary"):
    st.success("Your selections:")
    st.json(user_params)
