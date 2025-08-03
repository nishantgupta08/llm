import streamlit as st
import pandas as pd

def parameter_table(param_dict, task_name, param_category, get_ideal_value, get_ideal_value_reason):
    """
    Renders parameters as a table: Label | Info | Ideal Value | Reason | Widget.
    Returns a dict of param_name: value.
    """
    st.markdown("#### Parameters")
    headers = ["Label", "Info", "Ideal Value", "Reason", "Value"]
    cols = st.columns([2, 3, 2, 2, 3])
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    values = {}
    for p, cfg in param_dict.items():
        ideal = get_ideal_value(task_name, param_category, p)
        reason = get_ideal_value_reason(task_name, param_category, p)
        with cols[0]: st.markdown(cfg.get("label", p))
        with cols[1]: st.markdown(cfg.get("info", ""))
        with cols[2]: st.markdown(str(ideal) if ideal is not None else "")
        with cols[3]: st.markdown(str(reason) if reason is not None else "")
        with cols[4]:
            typ, options = cfg.get("type", "text"), cfg.get("options", [])
            if typ in ("dropdown", "select"):
                value = st.selectbox("", options, index=options.index(ideal) if ideal in options else 0, key=p)
            elif typ == "slider":
                value = st.slider("", cfg.get("min_value", 0), cfg.get("max_value", 100),
                                  value=ideal or cfg.get("min_value", 0), step=cfg.get("step", 1), key=p)
            elif typ == "checkbox":
                value = st.checkbox("", value=bool(ideal), key=p)
            elif typ == "number":
                value = st.number_input("", cfg.get("min_value", 0), cfg.get("max_value", 100),
                                       value=ideal or cfg.get("min_value", 0), step=cfg.get("step", 1), key=p)
            else:
                value = st.text_input("", value=str(ideal or ""), key=p)
            values[p] = value
    return values

def model_picker_table(models_df, key="model_picker"):
    """
    Display an interactive model table with a single radio button for selection.
    Returns the selected model (as pd.Series).
    """
    model_names = [f"{row['name']} ({row['type']})" for _, row in models_df.iterrows()]
    selected_idx = st.radio("Select a model:", options=list(models_df.index),
                            format_func=lambda i: model_names[i], key=key)
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    for i, row in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        with cols[0]:
            if i == selected_idx:
                st.markdown(":radio_button:", unsafe_allow_html=True)
            else:
                st.markdown("○", unsafe_allow_html=True)
        highlight = "background-color: #E3F2FD;" if i == selected_idx else ""
        for j, colname in enumerate(["name", "type", "size", "trained_on", "source", "description", "intended_use"], 1):
            cols[j].markdown(f"<div style='{highlight}'>{row[colname]}</div>", unsafe_allow_html=True)
    return models_df.loc[selected_idx]

def model_dropdown(label, model_list):
    """Dropdown for model selection. Works for dict or str models."""
    if not model_list:
        st.warning("No models available.")
        return None
    model_names = [m["name"] if isinstance(m, dict) else m for m in model_list]
    selected_name = st.selectbox(label, model_names)
    for m in model_list:
        if (isinstance(m, dict) and m["name"] == selected_name) or (isinstance(m, str) and m == selected_name):
            return m
    return selected_name
