import streamlit as st
from models_config import (
    ENCODER_ONLY_MODELS,
    DECODER_ONLY_MODELS,
    ENCODER_DECODER_MODELS
)
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from utils.ui_helper import (
    display_compact_widgets_table,
    model_table_selection
)

# --- Config: define what widgets to show for each task ---
TASK_CONFIG = {
    "RAG-based QA": {
        "preprocessing": True,
        "encoder": True,
        "decoder": False,
        "encoder_decoder": False,
    },
    "Normal QA": {
        "preprocessing": True,
        "encoder": False,
        "decoder": False,
        "encoder_decoder": True,
    },
    "Summarisation": {
        "preprocessing": True,
        "encoder": False,
        "decoder": False,
        "encoder_decoder": True,
    },
    "Custom Task": {
        "preprocessing": False,
        "encoder": True,
        "decoder": True,
        "encoder_decoder": True,
    }
}

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

# Task selection
task = st.radio("Choose task:", list(TASK_CONFIG.keys()))
cfg = TASK_CONFIG[task]

user_params = {}

# Preprocessing parameters
if cfg.get("preprocessing"):
    preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
    if preprocessing_params_list:
        with st.expander("⚙️ Preprocessing Parameters", expanded=True):
            user_params["preprocessing"] = display_compact_widgets_table(
                preprocessing_params_list, "Preprocessing Parameters"
            )

# Encoder model selection
if cfg.get("encoder"):
    with st.expander("🤖 Encoder Model Selection", expanded=True):
        user_params["encoder"] = model_table_selection(
            "Encoder Model", ENCODER_ONLY_MODELS, task, prefix="encoder"
        )

# Decoder model selection
if cfg.get("decoder"):
    with st.expander("🤖 Decoder Model Selection", expanded=True):
        user_params["decoder"] = model_table_selection(
            "Decoder Model", DECODER_ONLY_MODELS, task, prefix="decoder"
        )

# Encoder-Decoder model selection
if cfg.get("encoder_decoder"):
    with st.expander("🤖 Encoder-Decoder Model Selection", expanded=True):
        user_params["encoder_decoder"] = model_table_selection(
            "Encoder-Decoder Model", ENCODER_DECODER_MODELS, task, prefix="encdec"
        )

# Submit button
if st.button("🚀 Run Task", type="primary"):
    st.success("Selections submitted:")
    st.json(user_params)
