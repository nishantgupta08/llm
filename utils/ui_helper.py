import streamlit as st
import pandas as pd
from strategies.decoding_strategies import TASK_DECODING_PARAMS
from strategies.encoding_strategies import TASK_ENCODING_PARAMS, EncodingParam
from strategies.preprocessing_strategies import TASK_PREPROCESSING_PARAMS
from strategies.types import InputType, ValueType

def display_hint(ideal_value_reason: str, hint_type: str = "info", sidebar=False, description: str = ""):
    """
    Display a compact hint with tooltip-style information.
    Args:
        ideal_value_reason (str): The reason for the ideal value
        hint_type (str): Type of hint - "info", "warning", "success"
        sidebar (bool): If True, display in sidebar
        description (str): Optional description to show with hint
    """
    if not ideal_value_reason and not description:
        return
    
    icons = {
        "info": "💡",
        "warning": "⚠️", 
        "success": "✅",
        "decoding": "🎯",
        "encoding": "🔧",
        "preprocessing": "⚙️"
    }
    
    icon = icons.get(hint_type, "💡")
    
    # Create compact tooltip-style display
    if description and ideal_value_reason:
        tooltip_text = f"{description}\n\n💡 {ideal_value_reason}"
    elif description:
        tooltip_text = description
    elif ideal_value_reason:
        tooltip_text = f"💡 {ideal_value_reason}"
    else:
        return
    
    # Use a small, subtle indicator
    html = f"""<div style='
            display: inline-block;
            margin-left: 5px;
            cursor: help;
            font-size: 0.8em;
            opacity: 0.7;
        ' title="{tooltip_text}">
            {icon}
        </div>"""
    
    if sidebar:
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def display_compact_info(param, sidebar=False):
    """
    Display compact parameter information with smart formatting.
    """
    if not param.info and not param.ideal_value_reason:
        return
    
    # Create a compact info display
    info_parts = []
    if param.info:
        info_parts.append(param.info)
    if param.ideal_value_reason:
        info_parts.append(f"💡 {param.ideal_value_reason}")
    
    if info_parts:
        # Use a small info badge
        info_text = " | ".join(info_parts)
        html = f"""<div style='
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 6px;
                margin: 2px 0;
                font-size: 0.75em;
                color: #6c757d;
                display: inline-block;
            '>
                ℹ️ {info_text}
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
    
    # Display compact info instead of verbose hints
    if param.info or param.ideal_value_reason:
        display_compact_info(param, sidebar=True)
    
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

def display_parameters_table(params_list, title, sidebar=True):
    """
    Display parameters in a clean tabular format.
    
    Args:
        params_list: List of parameter objects
        title: Title for the parameter section
        sidebar: Whether to display in sidebar
    """
    if not params_list:
        return {}
    
    # Create a DataFrame for display
    table_data = []
    for param in params_list:
        # Handle different parameter types (EncodingParam vs DecodingParam)
        if hasattr(param, 'min_value'):
            # EncodingParam uses min_value, max_value
            range_str = f"{param.min_value}-{param.max_value}" if param.min_value and param.max_value else "N/A"
        elif hasattr(param, 'min'):
            # DecodingParam uses min, max
            range_str = f"{param.min}-{param.max}" if param.min is not None and param.max is not None else "N/A"
        else:
            range_str = "N/A"
        
        table_data.append({
            "Parameter": param.label,
            "Type": param.type.value,
            "Value": str(param.ideal),
            "Range": param.range if hasattr(param, 'range') and param.range else range_str,
            "Info": param.info[:50] + "..." if len(param.info) > 50 else param.info
        })
    
    df = pd.DataFrame(table_data)
    
    # Display the table
    if sidebar:
        st.sidebar.subheader(f"📋 {title}")
        st.sidebar.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.subheader(f"📋 {title}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Create widgets below the table
    params = {}
    for param in params_list:
        key = f"{title.lower().replace(' ', '_')}_{param.name}"
        
        # Choose the appropriate streamlit function based on sidebar parameter
        st_func = st.sidebar if sidebar else st
        
        if param.type == InputType.DROPDOWN:
            widget = st_func.selectbox(
                f"{param.label}",
                options=param.options,
                index=param.options.index(param.ideal) if param.ideal in param.options else 0,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key
            )
        elif param.type == InputType.CHECKBOX:
            widget = st_func.checkbox(
                param.label,
                value=param.ideal,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key
            )
        elif param.type == InputType.NUMBER:
            # Handle different parameter types
            if hasattr(param, 'min_value'):
                # EncodingParam
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
            else:
                # DecodingParam
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
            
            if hasattr(param, 'step') and param.step:
                step = param.step
            
            widget = st_func.number_input(
                param.label,
                min_value=min_val,
                max_value=max_val,
                value=ideal_val,
                step=step,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key
            )
        elif param.type == InputType.SLIDER:
            # Handle different parameter types
            if hasattr(param, 'min_value'):
                # EncodingParam
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
            else:
                # DecodingParam
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
            
            if hasattr(param, 'step') and param.step:
                step = param.step
            
            widget = st_func.slider(
                param.label,
                min_value=min_val,
                max_value=max_val,
                value=ideal_val,
                step=step,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key
            )
        else:
            continue
        
        params[param.name] = widget
    
    return params

def display_interactive_parameters_table(params_list, title, sidebar=True):
    """
    Display parameters in an interactive table with widgets embedded in the table.
    
    Args:
        params_list: List of parameter objects
        title: Title for the parameter section
        sidebar: Whether to display in sidebar
    """
    if not params_list:
        return {}
    
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
        import pandas as pd
        
        # Create a DataFrame for display
        table_data = []
        for i, param in enumerate(params_list):
            # Handle different parameter types (EncodingParam vs DecodingParam)
            if hasattr(param, 'min_value'):
                # EncodingParam uses min_value, max_value
                range_str = f"{param.min_value}-{param.max_value}" if param.min_value and param.max_value else "N/A"
            elif hasattr(param, 'min'):
                # DecodingParam uses min, max
                range_str = f"{param.min}-{param.max}" if param.min is not None and param.max is not None else "N/A"
            else:
                range_str = "N/A"
            
            table_data.append({
                "Parameter": param.label,
                "Type": param.type.value,
                "Current Value": str(param.ideal),
                "Range": param.range if hasattr(param, 'range') and param.range else range_str,
                "Info": param.info[:40] + "..." if len(param.info) > 40 else param.info,
                "Widget": f"widget_{i}",  # Placeholder for widget
                "param_index": i  # Store parameter index for reference
            })
        
        df = pd.DataFrame(table_data)
        
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_column("Parameter", header_name="Parameter", width=150, editable=False)
        gb.configure_column("Type", header_name="Type", width=100, editable=False)
        gb.configure_column("Current Value", header_name="Current Value", width=120, editable=False)
        gb.configure_column("Range", header_name="Range", width=100, editable=False)
        gb.configure_column("Info", header_name="Info", width=200, editable=False)
        gb.configure_column("Widget", header_name="Control", width=150, editable=True)
        
        grid_options = gb.build()
        
        # Display the grid
        if sidebar:
            st.sidebar.subheader(f"📋 {title}")
            grid_response = st.sidebar.agrid(
                df,
                gridOptions=grid_options,
                height=400,
                width='100%',
                update_mode=GridUpdateMode.VALUE_CHANGED,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                key=f"{title.lower().replace(' ', '_')}_grid"
            )
        else:
            st.subheader(f"📋 {title}")
            grid_response = st.agrid(
                df,
                gridOptions=grid_options,
                height=400,
                width='100%',
                update_mode=GridUpdateMode.VALUE_CHANGED,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                key=f"{title.lower().replace(' ', '_')}_grid"
            )
        
        # Create widgets below the table for better UX
        st.caption("💡 Adjust parameters using the controls below:")
        
        params = {}
        for i, param in enumerate(params_list):
            key = f"{title.lower().replace(' ', '_')}_{param.name}_{i}"
            
            # Create widget based on parameter type
            if param.type == InputType.DROPDOWN:
                widget = st.selectbox(
                    f"{param.label}",
                    options=param.options,
                    index=param.options.index(param.ideal) if param.ideal in param.options else 0,
                    help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                    key=key
                )
            elif param.type == InputType.CHECKBOX:
                widget = st.checkbox(
                    param.label,
                    value=param.ideal,
                    help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                    key=key
                )
            elif param.type == InputType.NUMBER:
                # Handle different parameter types
                if hasattr(param, 'min_value'):
                    # EncodingParam
                    if param.value_type == ValueType.FLOAT:
                        min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                    else:
                        min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
                else:
                    # DecodingParam
                    if param.value_type == ValueType.FLOAT:
                        min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
                    else:
                        min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
                
                if hasattr(param, 'step') and param.step:
                    step = param.step
                
                widget = st.number_input(
                    param.label,
                    min_value=min_val,
                    max_value=max_val,
                    value=ideal_val,
                    step=step,
                    help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                    key=key
                )
            elif param.type == InputType.SLIDER:
                # Handle different parameter types
                if hasattr(param, 'min_value'):
                    # EncodingParam
                    if param.value_type == ValueType.FLOAT:
                        min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                    else:
                        min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
                else:
                    # DecodingParam
                    if param.value_type == ValueType.FLOAT:
                        min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
                    else:
                        min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
                
                if hasattr(param, 'step') and param.step:
                    step = param.step
                
                widget = st.slider(
                    param.label,
                    min_value=min_val,
                    max_value=max_val,
                    value=ideal_val,
                    step=step,
                    help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                    key=key
                )
            else:
                continue
            
            params[param.name] = widget
        
        return params
        
    except ImportError:
        st.error("Please install st-aggrid: `pip install streamlit-aggrid`")
        # Fallback to regular table display
        return display_parameters_table(params_list, title, sidebar)

def display_compact_widgets_table(params_list, title, sidebar=True):
    """
    Display parameters in a table format with widgets embedded inside table cells.
    
    Args:
        params_list: List of parameter objects
        title: Title for the parameter section
        sidebar: Whether to display in sidebar
    """
    if not params_list:
        return {}
    
    # Create header
    if sidebar:
        st.sidebar.subheader(f"📋 {title}")
    else:
        st.subheader(f"📋 {title}")
    
    # Create a styled table with borders
    st.markdown("""
    <style>
    .param-table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
    }
    .param-table th, .param-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .param-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .param-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .param-table tr:hover {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create table header
    st.markdown("""
    <table class="param-table">
        <thead>
            <tr>
                <th>Parameter</th>
                <th>Type</th>
                <th>Range</th>
                <th>Control</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    params = {}
    for i, param in enumerate(params_list):
        # Handle different parameter types for range
        if hasattr(param, 'min_value'):
            range_str = f"{param.min_value}-{param.max_value}" if param.min_value and param.max_value else "N/A"
        elif hasattr(param, 'min'):
            range_str = f"{param.min}-{param.max}" if param.min is not None and param.max is not None else "N/A"
        else:
            range_str = "N/A"
        
        # Create table row
        st.markdown(f"""
        <tr>
            <td><strong>{param.label}</strong><br><small>{param.info[:50]}{'...' if len(param.info) > 50 else ''}</small></td>
            <td><code>{param.type.value}</code></td>
            <td><code>{range_str}</code></td>
            <td>
        """, unsafe_allow_html=True)
        
        # Create widget in the table cell
        key = f"{title.lower().replace(' ', '_')}_{param.name}_{i}"
        
        # Create widget based on parameter type
        if param.type == InputType.DROPDOWN:
            widget = st.selectbox(
                "Value",
                options=param.options,
                index=param.options.index(param.ideal) if param.ideal in param.options else 0,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key,
                label_visibility="collapsed"
            )
        elif param.type == InputType.CHECKBOX:
            widget = st.checkbox(
                "Value",
                value=param.ideal,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key,
                label_visibility="collapsed"
            )
        elif param.type == InputType.NUMBER:
            # Handle different parameter types
            if hasattr(param, 'min_value'):
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
            else:
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
            
            if hasattr(param, 'step') and param.step:
                step = param.step
            
            widget = st.number_input(
                "Value",
                min_value=min_val,
                max_value=max_val,
                value=ideal_val,
                step=step,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key,
                label_visibility="collapsed"
            )
        elif param.type == InputType.SLIDER:
            # Handle different parameter types
            if hasattr(param, 'min_value'):
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min_value), float(param.max_value), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min_value), int(param.max_value), int(param.ideal), 1
            else:
                if param.value_type == ValueType.FLOAT:
                    min_val, max_val, ideal_val, step = float(param.min), float(param.max), float(param.ideal), 0.01
                else:
                    min_val, max_val, ideal_val, step = int(param.min), int(param.max), int(param.ideal), 1
            
            if hasattr(param, 'step') and param.step:
                step = param.step
            
            widget = st.slider(
                "Value",
                min_value=min_val,
                max_value=max_val,
                value=ideal_val,
                step=step,
                help=f"{param.info} 💡 {param.ideal_value_reason}" if param.ideal_value_reason else param.info,
                key=key,
                label_visibility="collapsed"
            )
        else:
            continue
        
        params[param.name] = widget
        
        # Close table row
        st.markdown("</td></tr>", unsafe_allow_html=True)
    
    # Close table
    st.markdown("</tbody></table>", unsafe_allow_html=True)
    
    return params