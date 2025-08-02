import streamlit as st
import pandas as pd


def model_dropdown(label, model_list):
    """Dropdown for model selection. Returns the selected model name or None."""
    if not model_list:
        st.warning("No models available.")
        return None
    model_names = [m if isinstance(m, str) else getattr(m, "name", str(m)) for m in model_list]
    return st.selectbox(label, model_names)


def model_picker_table(models_df, key="model_picker"):
    """
    Display an interactive model table with a radio button for single selection.
    Returns the selected model (as pd.Series).
    """
    row_labels = [f"{row['name']} ({row['type']})" for _, row in models_df.iterrows()]
    selected_index = st.radio(
        "Select a model:", options=list(models_df.index),
        format_func=lambda i: row_labels[i], key=key
    )

    cols = st.columns([2, 2, 2, 2, 2, 2, 2])
    headers = ["Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")

    for i, model in models_df.iterrows():
        cols = st.columns([2, 2, 2, 2, 2, 2, 2])
        highlight = "background-color: #E3F2FD;" if i == selected_index else ""
        cols[0].markdown(f"<div style='{highlight}'>{model['name']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='{highlight}'>{model['type']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='{highlight}'>{model['size']}</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div style='{highlight}'>{model['trained_on']}</div>", unsafe_allow_html=True)
        cols[4].markdown(f"<div style='{highlight}'>{model['source']}</div>", unsafe_allow_html=True)
        cols[5].markdown(f"<div style='{highlight}'>{model['description']}</div>", unsafe_allow_html=True)
        cols[6].markdown(f"<div style='{highlight}'>{model['intended_use']}</div>", unsafe_allow_html=True)

    return models_df.loc[selected_index]


def model_picker_table_with_radio(models_df, key="model_picker_radio"):
    """
    Display an interactive model table with radio buttons integrated for single selection.
    Returns the selected model (as pd.Series) or None if no model is selected.
    """
    # Start table container with CSS class
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    
    # Create columns for the table with radio button in first column
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["Select", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f'<div class="model-table-header">{h}</div>', unsafe_allow_html=True)

    # Create radio options for model selection
    model_options = list(models_df.index)
    model_labels = [f"{row['name']} ({row['type']})" for _, row in models_df.iterrows()]
    
    # Use radio button for single selection
    selected_index = st.radio(
        "Choose a model:", 
        options=model_options,
        format_func=lambda i: model_labels[i],
        key=key,
        label_visibility="collapsed"  # Hide the label since we have headers
    )

    # Display the table with highlighting for selected row
    for i, model in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        
        # Highlight selected row
        row_class = "model-table-row selected" if i == selected_index else "model-table-row"
        
        # Radio button indicator with CSS class
        radio_class = "radio-indicator selected" if i == selected_index else "radio-indicator"
        cols[0].markdown(f'<div class="{radio_class}">●</div>' if i == selected_index else '<div class="radio-indicator">○</div>', unsafe_allow_html=True)
        
        # Model information in other columns with consistent height
        cols[1].markdown(f'<div class="{row_class} model-name">{model["name"]}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="{row_class}">{model["type"]}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="{row_class}">{model["size"]}</div>', unsafe_allow_html=True)
        cols[4].markdown(f'<div class="{row_class}">{model["trained_on"]}</div>', unsafe_allow_html=True)
        cols[5].markdown(f'<div class="{row_class}">{model["source"]}</div>', unsafe_allow_html=True)
        cols[6].markdown(f'<div class="{row_class} model-description">{model["description"]}</div>', unsafe_allow_html=True)
        cols[7].markdown(f'<div class="{row_class}">{model["intended_use"]}</div>', unsafe_allow_html=True)

    # End table container
    st.markdown('</div>', unsafe_allow_html=True)

    return models_df.loc[selected_index]


def model_picker_table_with_checkboxes(models_df, key="model_picker_checkbox"):
    """
    Display an interactive model table with checkboxes for selection.
    Returns the selected model (as pd.Series) or None if no model is selected.
    """
    # Create columns for the table with checkbox in first column
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["Select", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")

    selected_model = None
    
    for i, model in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        
        # Checkbox in first column
        is_selected = cols[0].checkbox("", key=f"{key}_{i}")
        
        # Model information in other columns
        cols[1].markdown(f"**{model['name']}**")
        cols[2].markdown(model['type'])
        cols[3].markdown(model['size'])
        cols[4].markdown(model['trained_on'])
        cols[5].markdown(model['source'])
        cols[6].markdown(model['description'])
        cols[7].markdown(model['intended_use'])
        
        # If this model is selected, store it
        if is_selected:
            selected_model = model
    
    return selected_model


def model_picker_table_multi_select(models_df, key="model_picker_multi"):
    """
    Display an interactive model table with checkboxes for multi-selection.
    Returns a list of selected models (as pd.Series objects).
    """
    # Create columns for the table with checkbox in first column
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["Select", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")

    selected_models = []
    
    for i, model in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        
        # Checkbox in first column
        is_selected = cols[0].checkbox("", key=f"{key}_{i}")
        
        # Model information in other columns
        cols[1].markdown(f"**{model['name']}**")
        cols[2].markdown(model['type'])
        cols[3].markdown(model['size'])
        cols[4].markdown(model['trained_on'])
        cols[5].markdown(model['source'])
        cols[6].markdown(model['description'])
        cols[7].markdown(model['intended_use'])
        
        # If this model is selected, add it to the list
        if is_selected:
            selected_models.append(model)
    
    return selected_models

    
def parameter_table(param_dict, task_name, param_category, get_ideal_value, get_ideal_value_reason):
    """
    Renders parameters as a table with columns: Label | Info | Ideal Value | Reason | Value.
    Returns a dict of param_name: value.
    Requires:
        - param_dict: dict of parameter configs
        - task_name: str
        - param_category: str
        - get_ideal_value: function
        - get_ideal_value_reason: function
    """
    st.markdown("#### Parameters")
    
    # Start parameter table container with CSS class
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    
    cols = st.columns([2, 3, 2, 2, 3])  # Adjust column width as needed
    headers = ["Label", "Info", "Ideal Value", "Reason", "Value"]
    
    # Header row with CSS styling
    for col, h in zip(cols, headers):
        col.markdown(f'<div class="parameter-table-header">{h}</div>', unsafe_allow_html=True)
    
    values = {}
    for p, cfg in param_dict.items():
        # Create a new row for each parameter
        cols = st.columns([2, 3, 2, 2, 3])
        
        # Parameter label
        cols[0].markdown(f'<div class="parameter-table-row">{cfg.get("label", p)}</div>', unsafe_allow_html=True)
        
        # Parameter info
        cols[1].markdown(f'<div class="parameter-table-row parameter-info">{cfg.get("info", "")}</div>', unsafe_allow_html=True)
        
        # Ideal value
        ideal = get_ideal_value(task_name, param_category, p)
        cols[2].markdown(f'<div class="parameter-table-row ideal-value">{str(ideal) if ideal is not None else ""}</div>', unsafe_allow_html=True)
        
        # Reason
        reason = get_ideal_value_reason(task_name, param_category, p)
        cols[3].markdown(f'<div class="parameter-table-row reason">{str(reason) if reason is not None else ""}</div>', unsafe_allow_html=True)
        
        # Value input widget
        with cols[4]:
            widget_type = cfg.get("type", "text")
            options = cfg.get("options", [])
            
            if widget_type in ("dropdown", "select"):
                value = st.selectbox("", options, index=options.index(ideal) if ideal in options else 0, key=p)
            elif widget_type == "slider":
                value = st.slider(
                    "", cfg.get("min_value", 0), cfg.get("max_value", 100),
                    value=ideal or cfg.get("min_value", 0), step=cfg.get("step", 1), key=p
                )
            elif widget_type == "checkbox":
                value = st.checkbox("", value=bool(ideal), key=p)
            elif widget_type == "number":
                value = st.number_input(
                    "", cfg.get("min_value", 0), cfg.get("max_value", 100),
                    value=ideal or cfg.get("min_value", 0), step=cfg.get("step", 1), key=p
                )
            else:
                value = st.text_input("", value=str(ideal or ""), key=p)
            
            values[p] = value
    
    # End parameter table container
    st.markdown('</div>', unsafe_allow_html=True)
    
    return values
