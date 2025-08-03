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


import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def aggrid_model_picker(models_df, key="aggrid_model_picker"):
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    gb = GridOptionsBuilder.from_dataframe(models_df)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    # (Column configs as before...)
    grid_options = gb.build()
    grid_return = AgGrid(
        models_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        key=key,
        height=min(500, 50 + 35 * len(models_df)),
        fit_columns_on_grid_load=False,
    )
    selected = None
    sel = grid_return["selected_rows"]
    # FIX: Check if sel is a DataFrame or list
    if isinstance(sel, pd.DataFrame):
        if not sel.empty:
            selected = sel.iloc[0].to_dict()
    elif isinstance(sel, list) and len(sel) > 0:
        selected = sel[0]
    return selected

# Example usage:
# models_df = pd.DataFrame(all_models)
# selected_model = aggrid_model_picker(models_df)
# if selected_model:
#     st.success(f"Selected model: {selected_model['name']}")
#     st.write(selected_model)

def single_select_radio_in_table(models_df, key="model_select"):
        # Build labels for the radio buttons (could be empty or custom)
    radio_labels = ["" for _ in models_df.index]
    selected_idx = st.radio(
        label="Select a model",
        options=list(models_df.index),
        format_func=lambda i: "",
        index=0,
        key=key
    )
    # Draw the table header (no header for first column, which is radio)
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    # For each row, show radio button as part of first column and highlight selection
    for i, row in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        # Place a fake "selected" radio icon (just visual), since st.radio only renders the selection group above
        with cols[0]:
            if i == selected_idx:
                st.markdown("🔘")
            else:
                st.markdown("⚪️")
        highlight = "background-color: #E3F2FD;" if i == selected_idx else ""
        for j, k in enumerate(["name", "type", "size", "trained_on", "source", "description", "intended_use"], 1):
            cols[j].markdown(f"<div style='{highlight}'>{row[k]}</div>", unsafe_allow_html=True)
    return models_df.loc[selected_idx]

def single_select_checkbox_table(models_df, key="model_select"):
    """
    Display a table of models with single-select checkboxes.
    Only one checkbox can be selected at a time.
    Returns the selected model (as pd.Series).
    """
    # Initialize session state for tracking selection
    selected_key = f"{key}_selected"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = None
    
    # Display table headers
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["Select", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    
    selected_model = None
    
    # Display each model row
    for i, model in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        
        # Create unique key for this checkbox
        checkbox_key = f"{key}_checkbox_{i}"
        
        # Determine if this checkbox should be checked
        is_checked = st.session_state[selected_key] == i
        
        # Create the checkbox
        if cols[0].checkbox("", value=is_checked, key=checkbox_key):
            # If this checkbox is now checked, update selection
            if st.session_state[selected_key] != i:
                st.session_state[selected_key] = i
                selected_model = model
        else:
            # If this checkbox is unchecked but was previously selected, keep it checked
            if st.session_state[selected_key] == i:
                # Force the checkbox to stay checked
                st.session_state[checkbox_key] = True
                selected_model = model
        
        # Highlight the selected row
        highlight = "background-color: #E3F2FD;" if st.session_state[selected_key] == i else ""
        
        # Display model information
        cols[1].markdown(f"<div style='{highlight}'><strong>{model['name']}</strong></div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='{highlight}'>{model['type']}</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div style='{highlight}'>{model['size']}</div>", unsafe_allow_html=True)
        cols[4].markdown(f"<div style='{highlight}'>{model['trained_on']}</div>", unsafe_allow_html=True)
        cols[5].markdown(f"<div style='{highlight}'>{model['source']}</div>", unsafe_allow_html=True)
        cols[6].markdown(f"<div style='{highlight}'>{model['description']}</div>", unsafe_allow_html=True)
        cols[7].markdown(f"<div style='{highlight}'>{model['intended_use']}</div>", unsafe_allow_html=True)
    
    # Return the selected model
    if selected_model is not None:
        return selected_model
    elif st.session_state[selected_key] is not None:
        # Return the model from session state if no new selection was made
        return models_df.iloc[st.session_state[selected_key]]
    else:
        return None


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
