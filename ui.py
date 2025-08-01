import streamlit as st
from models_config import (
    ENCODER_ONLY_MODELS,
    DECODER_ONLY_MODELS,
    ENCODER_DECODER_MODELS
)
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from strategies.encoding_strategies import TASK_ENCODING_PARAMS
from utils.ui_helper import (
    render_param_group,
    model_table_selection
)

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
    }
}

st.set_page_config(page_title="🧠 GenAI Playground", layout="wide")
st.title("🧠 GenAI Playground")

task = st.radio("Choose task:", list(TASK_CONFIG.keys()))
cfg = TASK_CONFIG[task]
user_params = {}

# Preprocessing parameters (if any)
if cfg.get("preprocessing"):
    preprocessing_params_list = TASK_PREPROCESSING_PARAMS.get(task, [])
    if preprocessing_params_list:
        user_params["preprocessing"] = render_param_group(
            preprocessing_params_list, "Preprocessing Parameters", key_prefix="pre", sidebar=False
        )

# Encoder model selection (AgGrid interactive)
if cfg.get("encoder"):
    encoder_obj = model_table_selection("Encoder Model", ENCODER_ONLY_MODELS, prefix="encoder")
    user_params["encoder"] = encoder_obj.name if encoder_obj else None

# Decoder model selection (AgGrid interactive)
if cfg.get("decoder"):
    decoder_obj = model_table_selection("Decoder Model", DECODER_ONLY_MODELS, prefix="decoder")
    user_params["decoder"] = decoder_obj.name if decoder_obj else None

# Encoder-Decoder model selection (AgGrid interactive)
if cfg.get("encoder_decoder"):
    encdec_obj = model_table_selection("Encoder-Decoder Model", ENCODER_DECODER_MODELS, prefix="encdec")
    user_params["encoder_decoder"] = encdec_obj.name if encdec_obj else None

# Encoding parameters (example)
if TASK_ENCODING_PARAMS.get(task):
    user_params["encoding"] = render_param_group(
        TASK_ENCODING_PARAMS[task], "Encoding Parameters", key_prefix="enc", sidebar=False
    )

# Submit button
if st.button("🚀 Run Task", type="primary"):
    st.success("Your selections:")
    st.json(user_params)
