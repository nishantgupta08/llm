import streamlit as st

def show_param_widget(param, key_prefix="", sidebar=False):
    key = f"{key_prefix}_{param.name}"
    st_func = st.sidebar if sidebar else st

    # Show info and reason as caption
    caption = f"{param.info or ''}".strip()
    if param.ideal_value_reason:
        caption += f"  💡 {param.ideal_value_reason}"
    if caption:
        st_func.caption(caption)

    # Widget selection
    if getattr(param, "type", None) in ["dropdown", "select"]:
        idx = param.options.index(param.ideal) if param.ideal in param.options else 0
        return st_func.selectbox(param.label, param.options, index=idx, key=key)
    elif param.type in ["slider"]:
        minv = getattr(param, "min_value", getattr(param, "min", 0))
        maxv = getattr(param, "max_value", getattr(param, "max", 100))
        step = getattr(param, "step", 1)
        value = param.ideal
        return st_func.slider(param.label, min_value=minv, max_value=maxv, value=value, step=step, key=key)
    elif param.type in ["checkbox"]:
        return st_func.checkbox(param.label, value=param.ideal, key=key)
    elif param.type in ["number"]:
        minv = getattr(param, "min_value", getattr(param, "min", 0))
        maxv = getattr(param, "max_value", getattr(param, "max", 100))
        step = getattr(param, "step", 1)
        value = param.ideal
        return st_func.number_input(param.label, min_value=minv, max_value=maxv, value=value, step=step, key=key)
    else:
        return st_func.text_input(param.label, value=str(param.ideal), key=key)

def render_param_group(param_list, group_title, key_prefix="", sidebar=False):
    st_func = st.sidebar if sidebar else st
    values = {}
    with st_func.expander(group_title, expanded=True):
        for param in param_list:
            values[param.name] = show_param_widget(param, key_prefix=key_prefix, sidebar=sidebar)
    return values

def model_table_selection(label, model_list, prefix=""):
    import pandas as pd
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
