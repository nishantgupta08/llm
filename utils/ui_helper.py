import streamlit as st

def show_param_widget(param, key_prefix="", sidebar=False):
    """Render a widget for any parameter with info and ideal value reason."""
    key = f"{key_prefix}_{param.name}"
    st_func = st.sidebar if sidebar else st

    # Caption with info and reason
    caption = f"{param.info or ''}".strip()
    if param.ideal_value_reason:
        caption += f"  💡 {param.ideal_value_reason}"

    if caption:
        st_func.caption(caption)

    # Select widget by type
    if getattr(param, "type", None) in ["dropdown", "select"]:
        idx = param.options.index(param.ideal) if param.ideal in param.options else 0
        return st_func.selectbox(param.label, param.options, index=idx, key=key)
    elif param.type in ["slider"]:
        minv = param.min_value if hasattr(param, "min_value") else param.min
        maxv = param.max_value if hasattr(param, "max_value") else param.max
        step = getattr(param, "step", 1)
        value = param.ideal
        return st_func.slider(param.label, min_value=minv, max_value=maxv, value=value, step=step, key=key)
    elif param.type in ["checkbox"]:
        return st_func.checkbox(param.label, value=param.ideal, key=key)
    elif param.type in ["number"]:
        minv = param.min_value if hasattr(param, "min_value") else param.min
        maxv = param.max_value if hasattr(param, "max_value") else param.max
        step = getattr(param, "step", 1)
        value = param.ideal
        return st_func.number_input(param.label, min_value=minv, max_value=maxv, value=value, step=step, key=key)
    else:
        return st_func.text_input(param.label, value=str(param.ideal), key=key)

def render_param_group(param_list, group_title, key_prefix="", sidebar=False):
    """Show a group of param widgets in an expander, return {param.name: value}."""
    st_func = st.sidebar if sidebar else st
    values = {}
    with st_func.expander(group_title, expanded=True):
        for param in param_list:
            values[param.name] = show_param_widget(param, key_prefix=key_prefix, sidebar=sidebar)
    return values

def model_table_selection(label, model_list, task=None, prefix=""):
    """Show a model select dropdown with info in expander, returns selected name."""
    model_names = [m.name for m in model_list]
    key = f"model_{prefix}_{label.lower().replace(' ', '_')}"
    selected_name = st.selectbox(label, model_names, key=key)
    selected_model = next((m for m in model_list if m.name == selected_name), None)
    if selected_model:
        with st.expander("Model Info", expanded=False):
            st.write(f"**Description:** {selected_model.description}")
            st.write(f"**Trained on:** {selected_model.trained_on}")
            st.write(f"**Size:** {selected_model.size}")
            st.write(f"**Intended use:** {selected_model.intended_use}")
            st.write(f"**Source:** {selected_model.source}")
    return selected_name
