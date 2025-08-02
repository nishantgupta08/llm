import streamlit as st

def display_compact_widgets_table(param_list, title="Parameters", sidebar=False):
    """
    Display a compact table of parameters with widgets.
    Returns dict of param.name -> value.
    """
    if sidebar:
        st.sidebar.markdown(f"### {title}")
    else:
        st.markdown(f"### {title}")
    
    param_values = {}
    for param in param_list:
        key = f"{title}_{param.name}"
        if getattr(param, "type", None) in ["dropdown", "select"]:
            idx = param.options.index(param.ideal) if hasattr(param, "options") and param.ideal in param.options else 0
            val = st.selectbox(param.label, param.options, index=idx, key=key)
        elif param.type in ["slider"]:
            minv = getattr(param, "min_value", getattr(param, "min", 0))
            maxv = getattr(param, "max_value", getattr(param, "max", 100))
            step = getattr(param, "step", 1)
            value = param.ideal
            val = st.slider(param.label, min_value=minv, max_value=maxv, value=value, step=step, key=key)
        elif param.type in ["checkbox"]:
            val = st.checkbox(param.label, value=param.ideal, key=key)
        elif param.type in ["number"]:
            minv = getattr(param, "min_value", getattr(param, "min", 0))
            maxv = getattr(param, "max_value", getattr(param, "max", 100))
            step = getattr(param, "step", 1)
            value = param.ideal
            val = st.number_input(param.label, min_value=minv, max_value=maxv, value=value, step=step, key=key)
        else:
            val = st.text_input(param.label, value=str(param.ideal), key=key)
        param_values[param.name] = val
    return param_values

def model_dropdown(label, model_list, task=None):
    """
    Create a dropdown for model selection.
    Returns the selected model name.
    """
    if not model_list:
        st.warning("No models available.")
        return None
    
    model_names = [m if isinstance(m, str) else m.name for m in model_list]
    selected = st.selectbox(label, model_names)
    return selected

def render_param_table(param_list, title="Parameters"):
    """
    Render a table of parameters with widgets in the last column.
    Info and Ideal Reason get separate color highlights.
    All rows have equal height for best alignment.
    Returns dict of param.name -> value.
    """
    st.markdown(f"### {title}")
    # Header row
    col1, col2, col3, col4 = st.columns([2,2,2,2])
    with col1: st.markdown("**Parameter**")
    with col2: st.markdown("**Info**")
    with col3: st.markdown("**Ideal Reason**")
    with col4: st.markdown("**Value**")

    st.markdown(
        """
        <style>
        .param-info-cell {
            background-color: #E3F2FD; color: #1a237e; border-radius: 4px;
            padding: 8px 8px; min-height: 48px; display: flex; align-items: center;
            font-size: 0.95em; margin-bottom: 2px;
        }
        .param-ideal-cell {
            background-color: #E8F5E9; color: #256029; border-radius: 4px;
            padding: 8px 8px; min-height: 48px; display: flex; align-items: center;
            font-size: 0.95em; margin-bottom: 2px;
        }
        .param-label-cell {
            min-height: 48px; display: flex; align-items: center;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    param_values = {}
    for param in param_list:
        c1, c2, c3, c4 = st.columns([2,2,2,2])
        with c1:
            st.markdown(f"<div class='param-label-cell'>{param.label}</div>", unsafe_allow_html=True)
        with c2:
            info_html = f"<div class='param-info-cell'>{param.info or ''}</div>"
            st.markdown(info_html, unsafe_allow_html=True)
        with c3:
            reason_html = f"<div class='param-ideal-cell'>{param.ideal_value_reason or ''}</div>"
            st.markdown(reason_html, unsafe_allow_html=True)
        with c4:
            key = f"{title}_{param.name}"
            if getattr(param, "type", None) in ["dropdown", "select"]:
                idx = param.options.index(param.ideal) if hasattr(param, "options") and param.ideal in param.options else 0
                val = st.selectbox("", param.options, index=idx, key=key, label_visibility="collapsed")
            elif param.type in ["slider"]:
                minv = getattr(param, "min_value", getattr(param, "min", 0))
                maxv = getattr(param, "max_value", getattr(param, "max", 100))
                step = getattr(param, "step", 1)
                value = param.ideal
                val = st.slider("", min_value=minv, max_value=maxv, value=value, step=step, key=key, label_visibility="collapsed")
            elif param.type in ["checkbox"]:
                val = st.checkbox("", value=param.ideal, key=key, label_visibility="collapsed")
            elif param.type in ["number"]:
                minv = getattr(param, "min_value", getattr(param, "min", 0))
                maxv = getattr(param, "max_value", getattr(param, "max", 100))
                step = getattr(param, "step", 1)
                value = param.ideal
                val = st.number_input("", min_value=minv, max_value=maxv, value=value, step=step, key=key, label_visibility="collapsed")
            else:
                val = st.text_input("", value=str(param.ideal), key=key, label_visibility="collapsed")
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
