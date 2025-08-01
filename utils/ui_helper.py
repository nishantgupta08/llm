import streamlit as st

def render_param_table(param_list, title="Parameters"):
    """
    Render a table of parameters with widgets in the last column.
    Args:
        param_list: List of parameter objects, each with .label, .type, .ideal, .info, .ideal_value_reason, .options, etc.
        title: Title of the section.
    Returns:
        dict: {param.name: value} for all user inputs.
    """
    st.markdown(f"### {title}")
    # Header row
    col1, col2, col3, col4 = st.columns([2,2,2,2])
    col1.markdown("**Parameter**")
    col2.markdown("**Info**")
    col3.markdown("**Ideal Reason**")
    col4.markdown("**Value**")
    param_values = {}
    for param in param_list:
        c1, c2, c3, c4 = st.columns([2,2,2,2])
        c1.write(param.label)
        c2.caption(param.info or "")
        c3.caption(param.ideal_value_reason or "")
        key = f"{title}_{param.name}"
        # Widget selection logic
        if getattr(param, "type", None) in ["dropdown", "select"]:
            idx = param.options.index(param.ideal) if hasattr(param, "options") and param.ideal in param.options else 0
            val = c4.selectbox("", param.options, index=idx, key=key)
        elif param.type in ["slider"]:
            minv = getattr(param, "min_value", getattr(param, "min", 0))
            maxv = getattr(param, "max_value", getattr(param, "max", 100))
            step = getattr(param, "step", 1)
            value = param.ideal
            val = c4.slider("", min_value=minv, max_value=maxv, value=value, step=step, key=key)
        elif param.type in ["checkbox"]:
            val = c4.checkbox("", value=param.ideal, key=key)
        elif param.type in ["number"]:
            minv = getattr(param, "min_value", getattr(param, "min", 0))
            maxv = getattr(param, "max_value", getattr(param, "max", 100))
            step = getattr(param, "step", 1)
            value = param.ideal
            val = c4.number_input("", min_value=minv, max_value=maxv, value=value, step=step, key=key)
        else:
            val = c4.text_input("", value=str(param.ideal), key=key)
        param_values[param.name] = val
    return param_values

def model_table_selection(label, model_list, prefix=""):
    """
    Show an interactive AgGrid table for model selection, fallback to selectbox.
    Returns the selected model object (or None).
    """
    import pandas as pd
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder
        if not model_list:
            st.warning("No models available.")
            return None
        df = pd.DataFrame([m.__dict__ for m in model_list])
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection('single', use_checkbox=True)
        grid_options = gb.build()
        st.subheader(f"📋 {label}")
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            height=300,
            width='100%',
            update_mode='SELECTION_CHANGED',
            key=f"{prefix}_model_grid"
        )
        selected = grid_response['selected_rows']
        if selected:
            st.success(f"✅ Selected: {selected[0]['name']}")
            return next((m for m in model_list if m.name == selected[0]['name']), None)
        else:
            st.info("Please select a model from the table.")
            return None
    except ImportError:
        # Fallback: selectbox if AgGrid not available
        st.info("(AgGrid not installed: showing selectbox instead)")
        model_names = [m.name for m in model_list]
        selected_name = st.selectbox(label, model_names, key=f"{prefix}_fallback_select")
        return next((m for m in model_list if m.name == selected_name), None)
