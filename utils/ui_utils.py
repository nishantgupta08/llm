import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import json
import os

def ensure_slider_types(min_val, max_val, step, current_val):
    """
    Ensure consistent types for slider widget parameters
    Returns tuple of (min_val, max_val, step, current_val) with consistent types
    """
    if isinstance(step, float) or any(isinstance(x, float) for x in [min_val, max_val, current_val]):
        # Convert all to float if any is float
        return float(min_val), float(max_val), float(step), float(current_val)
    else:
        # Convert all to int if all are integers
        return int(min_val), int(max_val), int(step), int(current_val)

def aggrid_model_picker(models_df, key="aggrid_model_picker"):
    """Show models as a single-select AgGrid table. Returns the selected row as dict or None."""
    gb = GridOptionsBuilder.from_dataframe(models_df)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    grid_options = gb.build()
    grid_return = AgGrid(
        models_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        key=key,
        height=min(500, 50 + 35 * len(models_df)),
        fit_columns_on_grid_load=True,
    )
    sel = grid_return["selected_rows"]
    if isinstance(sel, pd.DataFrame):
        return sel.iloc[0].to_dict() if not sel.empty else None
    elif isinstance(sel, list) and sel:
        return sel[0]
    return None

def display_parameter_doc_sidebar(param_doc):
    """
    Display parameter documentation in a compact sidebar format with interactive widgets
    """
    # Description
    if param_doc.get('description'):
        st.markdown(f"**Description:** {param_doc['description']}")
    
    # Mathematical definition
    if param_doc.get('mathematical_definition'):
        st.markdown("**Mathematical Definition:**")
        st.code(param_doc['mathematical_definition'], language='text')
    
    # Use cases
    if param_doc.get('use_cases'):
        st.markdown("**Use Cases:**")
        for use_case in param_doc['use_cases'][:3]:  # Show first 3
            st.markdown(f"• {use_case}")
        if len(param_doc['use_cases']) > 3:
            st.markdown(f"*... and {len(param_doc['use_cases']) - 3} more*")
    
    # Options (for parameters with multiple options) - with interactive widgets
    if param_doc.get('options'):
        st.markdown("**Available Options:**")
        
        # Create a selectbox for option selection
        option_names = list(param_doc['options'].keys())
        option_labels = [param_doc['options'][key].get('name', key) for key in option_names]
        
        selected_option = st.selectbox(
            "Select an option:",
            option_labels,
            key=f"option_selector_{param_doc.get('name', 'param')}"
        )
        
        # Show details for selected option
        selected_option_key = option_names[option_labels.index(selected_option)]
        option_info = param_doc['options'][selected_option_key]
        
        with st.expander(f"**{option_info.get('name', selected_option_key)}**", expanded=True):
            st.markdown(option_info.get('description', ''))
            
            if option_info.get('mathematical_definition'):
                st.markdown("**Mathematical Definition:**")
                st.code(option_info['mathematical_definition'], language='text')
            
            if option_info.get('use_cases'):
                st.markdown("**Use Cases:**")
                for use_case in option_info['use_cases']:
                    st.markdown(f"• {use_case}")
            
            if option_info.get('advantages'):
                st.markdown("**Advantages:**")
                for advantage in option_info['advantages']:
                    st.markdown(f"✅ {advantage}")
            
            if option_info.get('disadvantages'):
                st.markdown("**Disadvantages:**")
                for disadvantage in option_info['disadvantages']:
                    st.markdown(f"❌ {disadvantage}")
            
            if option_info.get('recommended_for'):
                st.markdown("**Recommended For:**")
                for rec in option_info['recommended_for']:
                    st.markdown(f"🎯 {rec}")
            
            if option_info.get('not_recommended_for'):
                st.markdown("**Not Recommended For:**")
                for not_rec in option_info['not_recommended_for']:
                    st.markdown(f"⚠️ {not_rec}")
    
    # Interactive widgets for parameter values
    st.markdown("---")
    st.markdown("**Parameter Configuration:**")
    
    # Determine parameter type and create appropriate widget
    param_name = param_doc.get('name', 'parameter')
    
    # Check if this is a boolean parameter (like FP16)
    if 'precision' in param_name.lower() or 'fp16' in param_name.lower():
        # Checkbox for boolean parameters
        value = st.checkbox(
            f"Enable {param_name}",
            value=False,
            key=f"widget_{param_name}"
        )
        st.markdown(f"**Current Value:** {value}")
    
    # Check if this has recommended values for sliders
    elif param_doc.get('recommended_values'):
        # Create slider based on recommended values
        if isinstance(param_doc['recommended_values'], dict):
            # Find a numeric range from recommended values
            numeric_values = []
            for category, values in param_doc['recommended_values'].items():
                if isinstance(values, list):
                    numeric_values.extend(values)
                elif isinstance(values, (int, float)):
                    numeric_values.append(values)
            
            if numeric_values:
                min_val = min(numeric_values)
                max_val = max(numeric_values)
                default_val = numeric_values[0] if numeric_values else min_val
                
                value = st.slider(
                    f"Select {param_name}:",
                    min_value=float(min_val),
                    max_value=float(max_val),
                    value=float(default_val),
                    step=0.1 if any(isinstance(v, float) for v in numeric_values) else 1.0,
                    key=f"widget_{param_name}"
                )
                st.markdown(f"**Current Value:** {value}")
            else:
                # Fallback to text input
                value = st.text_input(
                    f"Enter {param_name}:",
                    value="",
                    key=f"widget_{param_name}"
                )
        else:
            value = st.text_input(
                f"Enter {param_name}:",
                value="",
                key=f"widget_{param_name}"
            )
    
    # Check if this has options for dropdown
    elif param_doc.get('options'):
        # Dropdown for parameters with options
        option_names = list(param_doc['options'].keys())
        option_labels = [param_doc['options'][key].get('name', key) for key in option_names]
        
        value = st.selectbox(
            f"Select {param_name}:",
            option_labels,
            key=f"widget_{param_name}"
        )
        st.markdown(f"**Current Value:** {value}")
    
    else:
        # Default text input
        value = st.text_input(
            f"Enter {param_name}:",
            value="",
            key=f"widget_{param_name}"
        )
        st.markdown(f"**Current Value:** {value}")
    
    # Advantages and disadvantages
    if param_doc.get('advantages'):
        st.markdown("**Advantages:**")
        if isinstance(param_doc['advantages'], dict):
            for category, items in param_doc['advantages'].items():
                st.markdown(f"**{category.title()}:**")
                for item in items[:2]:  # Show first 2
                    st.markdown(f"✅ {item}")
        else:
            for advantage in param_doc['advantages'][:3]:  # Show first 3
                st.markdown(f"✅ {advantage}")
    
    if param_doc.get('disadvantages'):
        st.markdown("**Disadvantages:**")
        if isinstance(param_doc['disadvantages'], dict):
            for category, items in param_doc['disadvantages'].items():
                st.markdown(f"**{category.title()}:**")
                for item in items[:2]:  # Show first 2
                    st.markdown(f"❌ {item}")
        else:
            for disadvantage in param_doc['disadvantages'][:3]:  # Show first 3
                st.markdown(f"❌ {disadvantage}")
    
    # Recommended values
    if param_doc.get('recommended_values'):
        st.markdown("**Recommended Values:**")
        for category, values in param_doc['recommended_values'].items():
            st.markdown(f"**{category.replace('_', ' ').title()}:** {values}")
    
    # Requirements
    if param_doc.get('requirements'):
        st.markdown("**Requirements:**")
        for requirement in param_doc['requirements']:
            st.markdown(f"🔧 {requirement}")
    
    # Operations (for preprocessing)
    if param_doc.get('operations'):
        st.markdown("**Operations:**")
        for operation in param_doc['operations']:
            st.markdown(f"🔧 {operation}")

def create_preprocessing_table(params, task):
    """
    Create a simple expandable table for preprocessing parameters with expandable parameter names for details and sliders/dropdowns for values
    """
    st.subheader("📝 Preprocessing Parameters")
    
    with st.expander("Configure Preprocessing Parameters", expanded=True):
        # Load parameter documentation for tooltips
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        doc_path = os.path.join(config_dir, "parameter_documentation.json")
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
        except:
            doc_data = {}
        
        param_values = {}
        
        for name, cfg in params.items():
            # Get documentation for this parameter
            param_doc = doc_data.get("preprocessing_parameters", {}).get(name, {})
            
            # Create expandable section for each parameter
            with st.expander(f"**{cfg.get('label', name)}** - {cfg.get('info', '')}", expanded=False):
                
                # Show parameter description
                st.markdown(f"**Description:** {cfg.get('info', '')}")
                
                # Show documentation if available
                if param_doc:
                    with st.expander("📖 Parameter Documentation", expanded=False):
                        display_parameter_doc_sidebar(param_doc)
                
                # Create appropriate widgets based on parameter type
                val_key = f"preprocessing_{name}_val"
                ideal = cfg.get("ideal", "")
                typ = cfg.get("type", "text")
                options = cfg.get("options", [])
                
                # Initialize session state if not exists
                if val_key not in st.session_state:
                    if typ in ["number", "slider"]:
                        st.session_state[val_key] = int(ideal) if str(ideal).isdigit() else 0
                    elif typ == "checkbox":
                        st.session_state[val_key] = bool(ideal)
                    else:
                        st.session_state[val_key] = ideal
                
                if typ == "checkbox":
                    # Single checkbox for boolean parameters
                    value = st.checkbox(
                        "Enable",
                        value=st.session_state[val_key],
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                elif typ in ("dropdown", "select") and options:
                    # Radio buttons for option selection
                    st.markdown("**Select Option:**")
                    selected_option = st.radio(
                        "Choose an option:",
                        options,
                        index=options.index(st.session_state[val_key]) if st.session_state[val_key] in options else 0,
                        key=f"radio_{val_key}"
                    )
                    st.session_state[val_key] = selected_option
                    param_values[name] = selected_option
                    
                    # Show details for selected option if documentation available
                    if param_doc and param_doc.get('options') and selected_option in param_doc['options']:
                        option_doc = param_doc['options'][selected_option]
                        with st.expander(f"Details for {selected_option}", expanded=False):
                            st.markdown(option_doc.get('description', ''))
                            if option_doc.get('advantages'):
                                st.markdown("**Advantages:**")
                                for advantage in option_doc['advantages']:
                                    st.markdown(f"✅ {advantage}")
                            if option_doc.get('disadvantages'):
                                st.markdown("**Disadvantages:**")
                                for disadvantage in option_doc['disadvantages']:
                                    st.markdown(f"❌ {disadvantage}")
                
                elif typ == "slider":
                    # Slider for numeric ranges
                    min_val = cfg.get("min", 0)  # Use "min" from config
                    max_val = cfg.get("max", 100)  # Use "max" from config
                    step = cfg.get("step", 1)  # Use "step" from config
                    
                    # Ensure consistent types for slider
                    min_val, max_val, step, current_val = ensure_slider_types(min_val, max_val, step, st.session_state[val_key])
                    
                    value = st.slider(
                        "Adjust value:",
                        min_value=min_val,
                        max_value=max_val,
                        value=current_val,
                        step=step,
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                elif typ == "number":
                    # Number input for specific values
                    min_val = cfg.get("min", 0)  # Use "min" from config
                    max_val = cfg.get("max", 100)  # Use "max" from config
                    step = cfg.get("step", 1)  # Use "step" from config
                    
                    # Ensure consistent types for number input
                    min_val, max_val, step, current_val = ensure_slider_types(min_val, max_val, step, st.session_state[val_key])
                    
                    value = st.number_input(
                        "Enter value:",
                        min_value=min_val,
                        max_value=max_val,
                        value=current_val,
                        step=step,
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                else:
                    # Text input for other types
                    value = st.text_input(
                        "Enter value:",
                        value=st.session_state[val_key],
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                # Show current value
                st.markdown(f"**Current Value:** `{st.session_state[val_key]}`")
                
                # Show ideal value and reason
                ideal_value = cfg.get("ideal", "Not specified")
                ideal_reason = cfg.get("ideal_value_reason", "No reason provided")
                st.markdown(f"**Ideal Value:** `{ideal_value}`")
                st.markdown(f"**Reason:** {ideal_reason}")
        
        # Show all current values
        st.markdown("---")
        st.markdown("### Current Configuration")
        st.json(param_values)
        
        return param_values

def create_encoding_table(params, task):
    """
    Create a simple expandable table for encoding parameters with expandable parameter names for details and sliders/dropdowns for values
    """
    st.subheader("🔧 Encoding Parameters")
    
    with st.expander("Configure Encoding Parameters", expanded=True):
        # Load parameter documentation for tooltips
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        doc_path = os.path.join(config_dir, "parameter_documentation.json")
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
        except:
            doc_data = {}
        
        param_values = {}
        
        for name, cfg in params.items():
            # Get documentation for this parameter
            param_doc = doc_data.get("encoding_parameters", {}).get(name, {})
            
            # Create expandable section for each parameter
            with st.expander(f"**{cfg.get('label', name)}** - {cfg.get('info', '')}", expanded=False):
                
                # Show parameter description
                st.markdown(f"**Description:** {cfg.get('info', '')}")
                
                # Show documentation if available
                if param_doc:
                    with st.expander("📖 Parameter Documentation", expanded=False):
                        display_parameter_doc_sidebar(param_doc)
                
                # Create appropriate widgets based on parameter type
                val_key = f"encoding_{name}_val"
                ideal = cfg.get("ideal", "")
                typ = cfg.get("type", "text")
                options = cfg.get("options", [])
                
                # Initialize session state if not exists
                if val_key not in st.session_state:
                    if typ in ["number", "slider"]:
                        st.session_state[val_key] = int(ideal) if str(ideal).isdigit() else 0
                    elif typ == "checkbox":
                        st.session_state[val_key] = bool(ideal)
                    else:
                        st.session_state[val_key] = ideal
                
                if typ == "checkbox":
                    # Single checkbox for boolean parameters
                    value = st.checkbox(
                        "Enable",
                        value=st.session_state[val_key],
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                elif typ in ("dropdown", "select") and options:
                    # Radio buttons for option selection
                    st.markdown("**Select Option:**")
                    selected_option = st.radio(
                        "Choose an option:",
                        options,
                        index=options.index(st.session_state[val_key]) if st.session_state[val_key] in options else 0,
                        key=f"radio_{val_key}"
                    )
                    st.session_state[val_key] = selected_option
                    param_values[name] = selected_option
                    
                    # Show details for selected option if documentation available
                    if param_doc and param_doc.get('options') and selected_option in param_doc['options']:
                        option_doc = param_doc['options'][selected_option]
                        with st.expander(f"Details for {selected_option}", expanded=False):
                            st.markdown(option_doc.get('description', ''))
                            if option_doc.get('advantages'):
                                st.markdown("**Advantages:**")
                                for advantage in option_doc['advantages']:
                                    st.markdown(f"✅ {advantage}")
                            if option_doc.get('disadvantages'):
                                st.markdown("**Disadvantages:**")
                                for disadvantage in option_doc['disadvantages']:
                                    st.markdown(f"❌ {disadvantage}")
                
                elif typ == "slider":
                    # Slider for numeric ranges
                    min_val = cfg.get("min", 0)  # Use "min" from config
                    max_val = cfg.get("max", 100)  # Use "max" from config
                    step = cfg.get("step", 1)  # Use "step" from config
                    
                    # Ensure consistent types for slider
                    min_val, max_val, step, current_val = ensure_slider_types(min_val, max_val, step, st.session_state[val_key])
                    
                    value = st.slider(
                        "Adjust value:",
                        min_value=min_val,
                        max_value=max_val,
                        value=current_val,
                        step=step,
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                elif typ == "number":
                    # Number input for specific values
                    min_val = cfg.get("min", 0)  # Use "min" from config
                    max_val = cfg.get("max", 100)  # Use "max" from config
                    step = cfg.get("step", 1)  # Use "step" from config
                    
                    # Ensure consistent types for number input
                    min_val, max_val, step, current_val = ensure_slider_types(min_val, max_val, step, st.session_state[val_key])
                    
                    value = st.number_input(
                        "Enter value:",
                        min_value=min_val,
                        max_value=max_val,
                        value=current_val,
                        step=step,
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                else:
                    # Text input for other types
                    value = st.text_input(
                        "Enter value:",
                        value=st.session_state[val_key],
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                # Show current value
                st.markdown(f"**Current Value:** `{st.session_state[val_key]}`")
                
                # Show ideal value and reason
                ideal_value = cfg.get("ideal", "Not specified")
                ideal_reason = cfg.get("ideal_value_reason", "No reason provided")
                st.markdown(f"**Ideal Value:** `{ideal_value}`")
                st.markdown(f"**Reason:** {ideal_reason}")
        
        # Show all current values
        st.markdown("---")
        st.markdown("### Current Configuration")
        st.json(param_values)
        
        return param_values

def create_decoding_table(params, task):
    """
    Create a simple expandable table for decoding parameters with expandable parameter names for details and sliders/dropdowns for values
    """
    st.subheader("🎲 Decoding Parameters")
    
    with st.expander("Configure Decoding Parameters", expanded=True):
        # Load parameter documentation for tooltips
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        doc_path = os.path.join(config_dir, "parameter_documentation.json")
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
        except:
            doc_data = {}
        
        param_values = {}
        
        for name, cfg in params.items():
            # Get documentation for this parameter
            param_doc = doc_data.get("decoding_parameters", {}).get(name, {})
            
            # Create expandable section for each parameter
            with st.expander(f"**{cfg.get('label', name)}** - {cfg.get('info', '')}", expanded=False):
                
                # Show parameter description
                st.markdown(f"**Description:** {cfg.get('info', '')}")
                
                # Show documentation if available
                if param_doc:
                    with st.expander("📖 Parameter Documentation", expanded=False):
                        display_parameter_doc_sidebar(param_doc)
                
                # Create appropriate widgets based on parameter type
                val_key = f"decoding_{name}_val"
                ideal = cfg.get("ideal", "")
                typ = cfg.get("type", "text")
                options = cfg.get("options", [])
                
                # Initialize session state if not exists
                if val_key not in st.session_state:
                    if typ in ["number", "slider"]:
                        st.session_state[val_key] = int(ideal) if str(ideal).isdigit() else 0
                    elif typ == "checkbox":
                        st.session_state[val_key] = bool(ideal)
                    else:
                        st.session_state[val_key] = ideal
                
                if typ == "checkbox":
                    # Single checkbox for boolean parameters
                    value = st.checkbox(
                        "Enable",
                        value=st.session_state[val_key],
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                elif typ in ("dropdown", "select") and options:
                    # Radio buttons for option selection
                    st.markdown("**Select Option:**")
                    selected_option = st.radio(
                        "Choose an option:",
                        options,
                        index=options.index(st.session_state[val_key]) if st.session_state[val_key] in options else 0,
                        key=f"radio_{val_key}"
                    )
                    st.session_state[val_key] = selected_option
                    param_values[name] = selected_option
                    
                    # Show details for selected option if documentation available
                    if param_doc and param_doc.get('options') and selected_option in param_doc['options']:
                        option_doc = param_doc['options'][selected_option]
                        with st.expander(f"Details for {selected_option}", expanded=False):
                            st.markdown(option_doc.get('description', ''))
                            if option_doc.get('advantages'):
                                st.markdown("**Advantages:**")
                                for advantage in option_doc['advantages']:
                                    st.markdown(f"✅ {advantage}")
                            if option_doc.get('disadvantages'):
                                st.markdown("**Disadvantages:**")
                                for disadvantage in option_doc['disadvantages']:
                                    st.markdown(f"❌ {disadvantage}")
                
                elif typ == "slider":
                    # Slider for numeric ranges
                    min_val = cfg.get("min", 0)  # Use "min" from config
                    max_val = cfg.get("max", 100)  # Use "max" from config
                    step = cfg.get("step", 1)  # Use "step" from config
                    
                    # Ensure consistent types for slider
                    min_val, max_val, step, current_val = ensure_slider_types(min_val, max_val, step, st.session_state[val_key])
                    
                    value = st.slider(
                        "Adjust value:",
                        min_value=min_val,
                        max_value=max_val,
                        value=current_val,
                        step=step,
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                elif typ == "number":
                    # Number input for specific values
                    min_val = cfg.get("min", 0)  # Use "min" from config
                    max_val = cfg.get("max", 100)  # Use "max" from config
                    step = cfg.get("step", 1)  # Use "step" from config
                    
                    # Ensure consistent types for number input
                    min_val, max_val, step, current_val = ensure_slider_types(min_val, max_val, step, st.session_state[val_key])
                    
                    value = st.number_input(
                        "Enter value:",
                        min_value=min_val,
                        max_value=max_val,
                        value=current_val,
                        step=step,
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                else:
                    # Text input for other types
                    value = st.text_input(
                        "Enter value:",
                        value=st.session_state[val_key],
                        key=f"widget_{val_key}"
                    )
                    st.session_state[val_key] = value
                    param_values[name] = value
                
                # Show current value
                st.markdown(f"**Current Value:** `{st.session_state[val_key]}`")
                
                # Show ideal value and reason
                ideal_value = cfg.get("ideal", "Not specified")
                ideal_reason = cfg.get("ideal_value_reason", "No reason provided")
                st.markdown(f"**Ideal Value:** `{ideal_value}`")
                st.markdown(f"**Reason:** {ideal_reason}")
        
        # Show all current values
        st.markdown("---")
        st.markdown("### Current Configuration")
        st.json(param_values)
        
        return param_values
