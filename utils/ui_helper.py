import streamlit as st
import pandas as pd
from strategies.decoding_strategies import TASK_DECODING_PARAMS
from strategies.encoding_strategies import TASK_ENCODING_PARAMS, EncodingParam
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from strategies.types import InputType, ValueType

def display_hint(ideal_value_reason: str, hint_type: str = "info", sidebar=False, description: str = ""):
    """
    Display a styled hint with optional description above or below parameter widgets.
    Args:
        ideal_value_reason (str): The reason for the ideal value
        hint_type (str): Type of hint - "info", "warning", "success"
        sidebar (bool): If True, display in sidebar
        description (str): Optional description to show with hint
    """
    if not ideal_value_reason and not description:
        return
    colors = {
        "info": {"bg": "#f0f8ff", "border": "#1f77b4", "icon": "💡"},
        "warning": {"bg": "#fff3cd", "border": "#ffc107", "icon": "⚠️"},
        "success": {"bg": "#d1ecf1", "border": "#17a2b8", "icon": "💡"},
        "decoding": {"bg": "#f0f8ff", "border": "#1f77b4", "icon": "🎯"},
        "encoding": {"bg": "#fff3cd", "border": "#ffc107", "icon": "🔧"},
        "preprocessing": {"bg": "#d1ecf1", "border": "#17a2b8", "icon": "⚙️"}
    }
    color_scheme = colors.get(hint_type, colors["info"])
    
    # Build content with separate sections for description and ideal_value_reason
    content_parts = []
    if description:
        content_parts.append(f"<strong>Info:</strong> {description}")
    if ideal_value_reason:
        content_parts.append(f"<strong>Why this value:</strong> {ideal_value_reason}")
    
    content = "<br>".join(content_parts)
    
    html = f"""<div style='
            background-color: {color_scheme['bg']}; 
            padding: 8px; 
            border-radius: 5px; 
            border-left: 4px solid {color_scheme['border']}; 
            margin: 5px 0;
            font-size: 0.9em;
        '>
            <small>{color_scheme['icon']} {content}</small>
        </div>"""
    if sidebar:
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def get_param_values_ui(task: str, param_reference: dict) -> dict:
    """
    Render Streamlit UI for model parameters for a given task and return user-selected values.
    Args:
        task (str): Task name.
        param_reference (dict): Parameter reference dictionary.
    Returns:
        dict: User-selected parameter values.
    """
    df = pd.DataFrame(param_reference["tasks"][task]["parameters"])
    with st.expander("⚙️ Model Parameters", expanded=False):
        st.dataframe(
            df[["label", "effect", "ideal", "range"]], use_container_width=True
        )
        values = {}
        for _, p in df.iterrows():
            label = str(p["label"])
            val_type = int if p["value_type"] == "int" else float
            step = 1 if val_type == int else 0.01
            input_fn = st.slider if p["type"] == "slider" else st.number_input
            values[p["name"]] = input_fn(
                label,
                val_type(p["min"]),
                val_type(p["max"]),
                val_type(p["ideal"]),
                step=step,
            )
        return values

def _build_help_text(param_info: str, ideal_value_reason: str) -> str:
    """Helper function to build help text consistently."""
    help_text = param_info
    if ideal_value_reason:
        help_text += f" 💡 {ideal_value_reason}"
    return help_text

def _create_numeric_widget(param, key: str, help_text: str):
    """Helper function to create numeric widgets (slider or number_input)."""
    if param.value_type == ValueType.FLOAT:
        min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
    else:
        min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
    
    if param.type == InputType.SLIDER:
        return st.sidebar.slider(
            param.label, min_val, max_val, ideal_val, step=step, help=help_text, key=key
        )
    else:
        return st.sidebar.number_input(
            param.label, min_val, max_val, ideal_val, step=step, help=help_text, key=key
        )

def _create_widget_and_display_hint(param, key: str, hint_type: str, widget_creator_func):
    """Helper function to create widget and display hint if needed."""
    help_text = _build_help_text(param.info, param.ideal_value_reason)
    widget = widget_creator_func(param, key, help_text)
    
    if param.info or param.ideal_value_reason:
        display_hint(param.ideal_value_reason, hint_type, sidebar=True, description=param.info)
    
    return widget

def decoding_param_widgets(task, prefix=""):
    params = {}
    for param in TASK_DECODING_PARAMS.get(task, []):
        key = f"{prefix}decoding_{param.name}" if prefix else f"decoding_{param.name}"
        
        def create_decoding_widget(param, key, help_text):
            if param.type in [InputType.SLIDER, InputType.NUMBER]:
                return _create_numeric_widget(param, key, help_text)
            return None
        
        widget = _create_widget_and_display_hint(param, key, "decoding", create_decoding_widget)
        if widget is not None:
            params[param.name] = widget
    
    return params

def encoding_param_widgets(task, prefix=""):
    params = {}
    for param in TASK_ENCODING_PARAMS.get(task, []):
        key = f"{prefix}encoding_{param.name}" if prefix else f"encoding_{param.name}"
        
        def create_encoding_widget(param, key, help_text):
            if param.type == InputType.DROPDOWN:
                return st.sidebar.selectbox(
                    param.label,
                    options=param.options,
                    index=param.options.index(param.ideal) if param.ideal in param.options else 0,
                    help=help_text,
                    key=key
                )
            elif param.type == InputType.NUMBER:
                return st.sidebar.number_input(
                    param.label,
                    value=param.ideal,
                    min_value=param.min_value,
                    max_value=param.max_value,
                    step=param.step,
                    help=help_text,
                    key=key
                )
            elif param.type == InputType.CHECKBOX:
                return st.sidebar.checkbox(
                    param.label,
                    value=param.ideal,
                    help=help_text,
                    key=key
                )
            return None
        
        widget = _create_widget_and_display_hint(param, key, "encoding", create_encoding_widget)
        if widget is not None:
            params[param.name] = widget
    
    return params

def preprocessing_param_widgets(task, prefix=""):
    params = {}
    for param in TASK_PREPROCESSING_PARAMS.get(task, []):
        key = f"{prefix}preprocessing_{param.name}" if prefix else f"preprocessing_{param.name}"
        
        def create_preprocessing_widget(param, key, help_text):
            if param.type == InputType.DROPDOWN:
                if param.options:
                    return st.sidebar.selectbox(
                        param.label,
                        options=param.options,
                        index=param.options.index(param.ideal) if param.ideal in param.options else 0,
                        help=help_text,
                        key=key
                    )
                else:
                    return st.sidebar.text_input(
                        param.label,
                        value=param.ideal,
                        help=help_text,
                        key=key
                    )
            elif param.type == InputType.CHECKBOX:
                return st.sidebar.checkbox(
                    param.label,
                    value=param.ideal,
                    help=help_text,
                    key=key
                )
            elif param.type == InputType.NUMBER:
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
                
                if param.step:
                    step = param.step
                
                return st.sidebar.number_input(
                    param.label,
                    min_value=min_val,
                    max_value=max_val,
                    value=ideal_val,
                    step=step,
                    help=help_text,
                    key=key
                )
            elif param.type == InputType.SLIDER:
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
                
                if param.step:
                    step = param.step
                
                return st.sidebar.slider(
                    param.label,
                    min_value=min_val,
                    max_value=max_val,
                    value=ideal_val,
                    step=step,
                    help=help_text,
                    key=key
                )
            return None
        
        widget = _create_widget_and_display_hint(param, key, "preprocessing", create_preprocessing_widget)
        if widget is not None:
            params[param.name] = widget
    
    return params

def model_table_selection(label, model_list, task=None, prefix=""):
    """
    Display models in a table format with AgGrid for better selection.
    
    Args:
        label (str): Label for the model selection section
        model_list (List[ModelInfo]): List of available models
        task (str): Current task for context
        prefix (str): Prefix for unique keys
    
    Returns:
        str: Selected model name or None
    """
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder
        import pandas as pd
        
        st.subheader(f"📋 {label}")
        
        # Convert model list to DataFrame
        df = pd.DataFrame([m.__dict__ for m in model_list])
        
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection('single', use_checkbox=True)
        gb.configure_column("name", header_name="Model Name", width=200)
        gb.configure_column("size", header_name="Size", width=80)
        gb.configure_column("type", header_name="Type", width=120)
        gb.configure_column("intended_use", header_name="Use Case", width=150)
        gb.configure_column("description", header_name="Description", width=300)
        gb.configure_column("trained_on", header_name="Trained On", width=150)
        gb.configure_column("source", header_name="Source", width=100)
        
        grid_options = gb.build()
        
        # Display the grid
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            height=300,
            width='100%',
            update_mode='SELECTION_CHANGED',
            key=f"{prefix}_grid"
        )
        
        # Get selected row
        selected_row = grid_response['selected_rows']
        if selected_row is not None and len(selected_row) > 0:
            selected_model = selected_row.iloc[0]['name']
            st.success(f"✅ Selected: {selected_model}")
            return selected_model
        else:
            st.info("Please select a model from the table above.")
            return None
            
    except ImportError:
        st.error("Please install st-aggrid: `pip install streamlit-aggrid`")
        return None

def model_dropdown(label, model_list, task=None, encoding_widgets=None, decoding_widgets=None):
    model_names = [m.name for m in model_list]
    key = f"model_{label.lower().replace(' ', '_')}"
    
    # Debug: Show number of models available
    st.sidebar.write(f"📊 {label}: {len(model_names)} models available")
    
    selected_name = st.selectbox(label, model_names, key=key)
    selected_model = next((m for m in model_list if m.name == selected_name), None)
    
    if selected_model:
        with st.expander("Model Info", expanded=False):
            st.write(f"**Description:** {selected_model.description}")
            st.write(f"**Trained on:** {selected_model.trained_on}")
            st.write(f"**Size:** {selected_model.size}")
            st.write(f"**Intended use:** {selected_model.intended_use}")
            st.write(f"**Source:** {selected_model.source}")
        
        # Show model loaded status
        st.sidebar.success(f"✅ {label} loaded: {selected_name}")
    return selected_name