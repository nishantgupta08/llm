import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import json
import os

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
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

import streamlit as st

import streamlit as st

def make_reset_callback(val_key, ideal, typ):
    def callback():
        if typ in ["number", "slider"]:
            st.session_state[val_key] = int(ideal) if str(ideal).isdigit() else 0
        elif typ == "checkbox":
            st.session_state[val_key] = bool(ideal)
        else:
            st.session_state[val_key] = ideal
    return callback


def smart_param_table_with_reset(param_dict, title="Parameters"):
    WIDTHS = [3, 4, 3, 4]
    st.markdown(f"### {title}")
    header_cols = st.columns(WIDTHS)
    for col, h in zip(header_cols, ["Label", "Info", "Reason", "Value"]):
        col.markdown(f"**{h}**")

    # Load parameter documentation for tooltips
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    doc_path = os.path.join(config_dir, "parameter_documentation.json")
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
    except:
        doc_data = {}

    param_values = {}
    for name, cfg in param_dict.items():
        row_cols = st.columns(WIDTHS)
        
        # Determine parameter type for documentation lookup
        param_type = "encoding"  # default
        if "pooling" in name.lower() or title.lower() == "pooling":
            param_type = "pooling"
        elif title.lower() == "decoding":
            param_type = "decoding"
        elif title.lower() == "preprocessing":
            param_type = "preprocessing"
        
        # Get documentation for this parameter
        param_doc = None
        if param_type == "pooling":
            param_doc = doc_data.get("pooling_strategies", {}).get(name, {})
        elif param_type == "encoding":
            param_doc = doc_data.get("encoding_parameters", {}).get(name, {})
        elif param_type == "decoding":
            param_doc = doc_data.get("decoding_parameters", {}).get(name, {})
        elif param_type == "preprocessing":
            param_doc = doc_data.get("preprocessing_parameters", {}).get(name, {})
        
        # Display label with help tooltip if documentation exists
        with row_cols[0]:
            if param_doc:
                help_text = f"**{param_doc.get('name', name)}**\n\n{param_doc.get('description', '')}"
                if param_doc.get('use_cases'):
                    help_text += f"\n\n**Use Cases:**\n" + "\n".join([f"• {uc}" for uc in param_doc['use_cases'][:3]])
                if param_doc.get('advantages'):
                    if isinstance(param_doc['advantages'], list):
                        help_text += f"\n\n**Advantages:**\n" + "\n".join([f"✅ {adv}" for adv in param_doc['advantages'][:2]])
                    else:
                        help_text += f"\n\n**Advantages:**\n" + "\n".join([f"✅ {adv}" for adv in list(param_doc['advantages'].values())[0][:2]])
                
                st.markdown(f"{cfg.get('label', name)} ⓘ", help=help_text)
            else:
                st.markdown(cfg.get("label", name))
        
        with row_cols[1]: 
            st.markdown(cfg.get("info", ""))
        with row_cols[2]: 
            st.markdown(str(cfg.get("ideal_value_reason", "")))

        val_key = f"{title}_{name}_val"
        reset_key = f"{title}_{name}_reset"
        ideal = cfg.get("ideal", "")
        typ = cfg.get("type", "text")

        # Only set the initial value if not yet set, and cast to correct type
        if val_key not in st.session_state:
            if typ in ["number", "slider"]:
                st.session_state[val_key] = int(ideal) if str(ideal).isdigit() else 0
            elif typ == "checkbox":
                st.session_state[val_key] = bool(ideal)
            else:
                st.session_state[val_key] = ideal

        with row_cols[3]:
            c_val, c_reset = st.columns([4, 1])
            # -- Widget --
            if typ in ("dropdown", "select") and cfg.get("options"):
                options = cfg["options"]
                val = st.session_state[val_key]
                
                idx = options.index(val) if val in options else 0
                value = c_val.selectbox(
                    "", options, index=idx, key=val_key, label_visibility="collapsed"
                )
            elif typ == "slider":
                minv = int(cfg.get("min_value", 0))
                maxv = int(cfg.get("max_value", 100))
                step = max(1, int(cfg.get("step", 1)))
                try:
                    val = int(st.session_state[val_key])
                    
                except Exception:
                    val = minv

                if val < minv:
                    val = minv
                elif val > maxv:
                    val = maxv

                value = c_val.slider(
                    "", min_value=minv, max_value=maxv, value=val, step=step, key=val_key, label_visibility="collapsed"
                )
            elif typ == "checkbox":
                value = c_val.checkbox(
                    "", value=bool(st.session_state[val_key]), key=val_key, label_visibility="collapsed"
                )
            elif typ == "number":
                minv = int(cfg.get("min_value", 0))
                maxv = int(cfg.get("max_value", 100))
                step = max(1, int(cfg.get("step", 1)))
                try:
                    val = int(st.session_state[val_key])
                except Exception:
                    val = minv
                
                if val < minv:
                    val = minv
                elif val > maxv:
                    val = maxv
                value = c_val.number_input(
                    "Enter a value", min_value=minv, max_value=maxv, value=val, step=step, 
                    key=val_key, label_visibility="collapsed"
                )
            else:
                value = c_val.text_input(
                    "", value=str(st.session_state[val_key]), key=val_key, label_visibility="collapsed"
                )
            # -- Reset button with callback --
            c_reset.button("⟲", key=reset_key, help="Reset to ideal value",
                           on_click=make_reset_callback(val_key, ideal, typ))
            param_values[name] = value
    return param_values


def smart_param_table(param_dict, key="param_grid"):
    # Convert dict to DataFrame
    rows = []
    for name, cfg in param_dict.items():
        row = {
            "Parameter": cfg.get("label", name),
            "Info": cfg.get("info", ""),
            "Ideal": cfg.get("ideal", ""),
            "Reason": cfg.get("ideal_value_reason", ""),
            "Value": cfg.get("ideal", ""),
            "Type": cfg.get("type", ""),
            "Options": cfg.get("options", []),
            "Min": cfg.get("min_value", 0),
            "Max": cfg.get("max_value", 100),
            "Step": cfg.get("step", 1),
        }
        rows.append(row)
    df = pd.DataFrame(rows)

    gb = GridOptionsBuilder.from_dataframe(df)
    for i, row in df.iterrows():
        typ = row["Type"]
        if typ in ("dropdown", "select") and row["Options"]:
            gb.configure_column("Value", editable=True, cellEditor='agSelectCellEditor',
                               cellEditorParams={'values': row["Options"]})
        elif typ == "checkbox":
            gb.configure_column("Value", editable=True, cellEditor='agCheckboxCellEditor')
        elif typ == "slider":
            gb.configure_column("Value", editable=True, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=2)
        elif typ == "number":
            gb.configure_column("Value", editable=True, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=2)
        else:
            gb.configure_column("Value", editable=True)
    grid_options = gb.build()
    grid_return = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        key=key,
        fit_columns_on_grid_load=True,
        reload_data=True
    )
    out_df = grid_return["data"]
    # Return dict of param label (or name) to value
    return dict(zip(df["Parameter"], out_df["Value"]))

def aggrid_param_table(param_dict, key="aggrid_param_table"):
    """
    Show editable parameter table via AgGrid.
    param_dict: dict of param_name: {...fields...}
    Returns: dict of param_name: user_value
    """
    # Build param DataFrame
    param_rows = []
    for name, cfg in param_dict.items():
        param_rows.append({
            "Parameter": cfg.get("label", name),
            "Info": cfg.get("info", ""),
            "Ideal Value": cfg.get("ideal", ""),
            "Reason": cfg.get("ideal_value_reason", ""),
            "Value": cfg.get("ideal", ""),
            "Type": cfg.get("type", ""),
            "Options": cfg.get("options", []),
        })
    param_df = pd.DataFrame(param_rows)

    # Setup AgGrid editors for Value column
    gb = GridOptionsBuilder.from_dataframe(param_df)
    gb.configure_column("Value", editable=True)
    for idx, row in param_df.iterrows():
        if row["Type"] in ("dropdown", "select") and row["Options"]:
            gb.configure_column(
                "Value",
                cellEditor='agSelectCellEditor',
                cellEditorParams={'values': row["Options"]}
            )
        elif row["Type"] == "checkbox":
            gb.configure_column("Value", cellEditor='agCheckboxCellEditor')
    grid_options = gb.build()

    grid_return = AgGrid(
        param_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        key=key,
        reload_data=True
    )
    updated_df = grid_return["data"]
    # Map back to param names (use the "Parameter" column as key)
    param_values = dict(zip(param_df["Parameter"], updated_df["Value"]))
    return param_values

def aggrid_param_table_perfect(param_dict, key="aggrid_param_table"):
    """
    Like aggrid_param_table, but keeps param_name as the index for 1:1 mapping.
    Returns: dict of param_name: user_value
    """
    param_rows = []
    for name, cfg in param_dict.items():
        param_rows.append({
            "param_name": name,
            "Parameter": cfg.get("label", name),
            "Info": cfg.get("info", ""),
            "Ideal Value": cfg.get("ideal", ""),
            "Reason": cfg.get("ideal_value_reason", ""),
            "Value": cfg.get("ideal", ""),
            "Type": cfg.get("type", ""),
            "Options": cfg.get("options", []),
        })
    param_df = pd.DataFrame(param_rows)
    param_df.set_index("param_name", inplace=True)

    gb = GridOptionsBuilder.from_dataframe(param_df)
    gb.configure_column("Value", editable=True)
    for idx, row in param_df.iterrows():
        if row["Type"] in ("dropdown", "select") and row["Options"]:
            gb.configure_column(
                "Value",
                cellEditor='agSelectCellEditor',
                cellEditorParams={'values': row["Options"]}
            )
        elif row["Type"] == "checkbox":
            gb.configure_column("Value", cellEditor='agCheckboxCellEditor')
    grid_options = gb.build()

    grid_return = AgGrid(
        param_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        key=key,
        reload_data=True
    )
    updated_df = grid_return["data"]
    param_values = updated_df["Value"].to_dict()
    return param_values

def display_parameter_documentation():
    """
    Display comprehensive parameter documentation in an expandable format
    """
    # Load parameter documentation
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    doc_path = os.path.join(config_dir, "parameter_documentation.json")
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
    except FileNotFoundError:
        st.error("Parameter documentation file not found!")
        return
    except json.JSONDecodeError:
        st.error("Invalid JSON in parameter documentation file!")
        return
    except UnicodeDecodeError:
        st.error("Unicode decode error in parameter documentation file!")
        return

    st.markdown("## 📚 Parameter Documentation")
    st.markdown("Comprehensive guide to all available parameters and their configurations.")
    
    # Create tabs for different parameter categories
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Pooling Strategies", "🔧 Encoding Parameters", "🎲 Decoding Parameters", "📝 Preprocessing Parameters"])
    
    with tab1:
        display_pooling_strategies(doc_data.get("pooling_strategies", {}))
    
    with tab2:
        display_encoding_parameters(doc_data.get("encoding_parameters", {}))
    
    with tab3:
        display_decoding_parameters(doc_data.get("decoding_parameters", {}))
    
    with tab4:
        display_preprocessing_parameters(doc_data.get("preprocessing_parameters", {}))

def display_pooling_strategies(pooling_data):
    """Display pooling strategies documentation"""
    st.markdown("### Pooling Strategies")
    st.markdown("Different methods to combine token embeddings into a single vector representation.")
    
    for strategy_key, strategy_info in pooling_data.items():
        with st.expander(f"**{strategy_info.get('name', strategy_key)}** - {strategy_info.get('description', '')}"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Mathematical Definition:**")
                st.code(strategy_info.get('mathematical_definition', 'N/A'), language='text')
                
                st.markdown("**Use Cases:**")
                for use_case in strategy_info.get('use_cases', []):
                    st.markdown(f"• {use_case}")
                
                st.markdown("**Advantages:**")
                for advantage in strategy_info.get('advantages', []):
                    st.markdown(f"✅ {advantage}")
            
            with col2:
                st.markdown("**Disadvantages:**")
                for disadvantage in strategy_info.get('disadvantages', []):
                    st.markdown(f"❌ {disadvantage}")
                
                st.markdown("**Recommended For:**")
                for rec in strategy_info.get('recommended_for', []):
                    st.markdown(f"🎯 {rec}")
                
                st.markdown("**Not Recommended For:**")
                for not_rec in strategy_info.get('not_recommended_for', []):
                    st.markdown(f"⚠️ {not_rec}")

def display_encoding_parameters(encoding_data):
    """Display encoding parameters documentation"""
    st.markdown("### Encoding Parameters")
    st.markdown("Parameters that control how text is encoded into embeddings.")
    
    for param_key, param_info in encoding_data.items():
        with st.expander(f"**{param_info.get('name', param_key)}** - {param_info.get('description', '')}"):
            
            # Display mathematical definition if available
            if 'mathematical_definition' in param_info:
                st.markdown("**Mathematical Definition:**")
                st.code(param_info['mathematical_definition'], language='text')
            
            # Display use cases
            if 'use_cases' in param_info:
                st.markdown("**Use Cases:**")
                for use_case in param_info['use_cases']:
                    st.markdown(f"• {use_case}")
            
            # Handle options-based parameters
            if 'options' in param_info:
                st.markdown("**Available Options:**")
                for option_key, option_info in param_info['options'].items():
                    with st.expander(f"**{option_info.get('name', option_key)}**", expanded=False):
                        st.markdown(option_info.get('description', ''))
                        
                        if 'advantages' in option_info:
                            st.markdown("**Advantages:**")
                            for advantage in option_info['advantages']:
                                st.markdown(f"✅ {advantage}")
                        
                        if 'disadvantages' in option_info:
                            st.markdown("**Disadvantages:**")
                            for disadvantage in option_info['disadvantages']:
                                st.markdown(f"❌ {disadvantage}")
            
            # Display advantages/disadvantages for non-option parameters
            if 'advantages' in param_info and 'options' not in param_info:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Advantages:**")
                    if isinstance(param_info['advantages'], dict):
                        for category, items in param_info['advantages'].items():
                            st.markdown(f"**{category.title()}:**")
                            for item in items:
                                st.markdown(f"✅ {item}")
                    else:
                        for advantage in param_info['advantages']:
                            st.markdown(f"✅ {advantage}")
                
                with col2:
                    if 'disadvantages' in param_info:
                        st.markdown("**Disadvantages:**")
                        if isinstance(param_info['disadvantages'], dict):
                            for category, items in param_info['disadvantages'].items():
                                st.markdown(f"**{category.title()}:**")
                                for item in items:
                                    st.markdown(f"❌ {item}")
                        else:
                            for disadvantage in param_info['disadvantages']:
                                st.markdown(f"❌ {disadvantage}")
            
            # Display recommended values
            if 'recommended_values' in param_info:
                st.markdown("**Recommended Values:**")
                for category, values in param_info['recommended_values'].items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:** {values}")
            
            # Display requirements
            if 'requirements' in param_info:
                st.markdown("**Requirements:**")
                for requirement in param_info['requirements']:
                    st.markdown(f"🔧 {requirement}")

def display_decoding_parameters(decoding_data):
    """Display decoding parameters documentation"""
    st.markdown("### Decoding Parameters")
    st.markdown("Parameters that control text generation and output behavior.")
    
    for param_key, param_info in decoding_data.items():
        with st.expander(f"**{param_info.get('name', param_key)}** - {param_info.get('description', '')}"):
            
            # Display mathematical definition if available
            if 'mathematical_definition' in param_info:
                st.markdown("**Mathematical Definition:**")
                st.code(param_info['mathematical_definition'], language='text')
            
            # Display use cases
            if 'use_cases' in param_info:
                st.markdown("**Use Cases:**")
                for use_case in param_info['use_cases']:
                    st.markdown(f"• {use_case}")
            
            # Display advantages/disadvantages
            col1, col2 = st.columns(2)
            with col1:
                if 'advantages' in param_info:
                    st.markdown("**Advantages:**")
                    if isinstance(param_info['advantages'], dict):
                        for category, items in param_info['advantages'].items():
                            st.markdown(f"**{category.title()}:**")
                            for item in items:
                                st.markdown(f"✅ {item}")
                    else:
                        for advantage in param_info['advantages']:
                            st.markdown(f"✅ {advantage}")
            
            with col2:
                if 'disadvantages' in param_info:
                    st.markdown("**Disadvantages:**")
                    if isinstance(param_info['disadvantages'], dict):
                        for category, items in param_info['disadvantages'].items():
                            st.markdown(f"**{category.title()}:**")
                            for item in items:
                                st.markdown(f"❌ {item}")
                    else:
                        for disadvantage in param_info['disadvantages']:
                            st.markdown(f"❌ {disadvantage}")
            
            # Display recommended values
            if 'recommended_values' in param_info:
                st.markdown("**Recommended Values:**")
                for category, values in param_info['recommended_values'].items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:** {values}")

def display_preprocessing_parameters(preprocessing_data):
    """Display preprocessing parameters documentation"""
    st.markdown("### Preprocessing Parameters")
    st.markdown("Parameters that control how text is prepared before processing.")
    
    for param_key, param_info in preprocessing_data.items():
        with st.expander(f"**{param_info.get('name', param_key)}** - {param_info.get('description', '')}"):
            
            # Handle options-based parameters
            if 'options' in param_info:
                st.markdown("**Available Options:**")
                for option_key, option_info in param_info['options'].items():
                    with st.expander(f"**{option_info.get('name', option_key)}**", expanded=False):
                        st.markdown(option_info.get('description', ''))
                        
                        if 'advantages' in option_info:
                            st.markdown("**Advantages:**")
                            for advantage in option_info['advantages']:
                                st.markdown(f"✅ {advantage}")
                        
                        if 'disadvantages' in option_info:
                            st.markdown("**Disadvantages:**")
                            for disadvantage in option_info['disadvantages']:
                                st.markdown(f"❌ {disadvantage}")
                        
                        if 'recommended_for' in option_info:
                            st.markdown("**Recommended For:**")
                            for rec in option_info['recommended_for']:
                                st.markdown(f"🎯 {rec}")
            
            # Display use cases
            if 'use_cases' in param_info:
                st.markdown("**Use Cases:**")
                for use_case in param_info['use_cases']:
                    st.markdown(f"• {use_case}")
            
            # Display advantages/disadvantages for non-option parameters
            if 'advantages' in param_info and 'options' not in param_info:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Advantages:**")
                    if isinstance(param_info['advantages'], dict):
                        for category, items in param_info['advantages'].items():
                            st.markdown(f"**{category.title()}:**")
                            for item in items:
                                st.markdown(f"✅ {item}")
                    else:
                        for advantage in param_info['advantages']:
                            st.markdown(f"✅ {advantage}")
                
                with col2:
                    if 'disadvantages' in param_info:
                        st.markdown("**Disadvantages:**")
                        if isinstance(param_info['disadvantages'], dict):
                            for category, items in param_info['disadvantages'].items():
                                st.markdown(f"**{category.title()}:**")
                                for item in items:
                                    st.markdown(f"❌ {item}")
                        else:
                            for disadvantage in param_info['disadvantages']:
                                st.markdown(f"❌ {disadvantage}")
            
            # Display recommended values
            if 'recommended_values' in param_info:
                st.markdown("**Recommended Values:**")
                for category, values in param_info['recommended_values'].items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:** {values}")
            
            # Display operations (for text cleaning)
            if 'operations' in param_info:
                st.markdown("**Operations:**")
                for operation in param_info['operations']:
                    st.markdown(f"🔧 {operation}")
            
            # Display what gets removed (for special character removal)
            if 'what_gets_removed' in param_info:
                st.markdown("**What Gets Removed:**")
                for item in param_info['what_gets_removed']:
                    st.markdown(f"🗑️ {item}")

def display_parameter_help_tooltip(param_name, param_type="encoding"):
    """
    Display a help tooltip for a specific parameter
    Returns HTML for use in st.markdown with unsafe_allow_html=True
    """
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    doc_path = os.path.join(config_dir, "parameter_documentation.json")
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
    except:
        return ""
    
    # Get parameter info based on type
    if param_type == "pooling":
        param_info = doc_data.get("pooling_strategies", {}).get(param_name, {})
    elif param_type == "encoding":
        param_info = doc_data.get("encoding_parameters", {}).get(param_name, {})
    elif param_type == "decoding":
        param_info = doc_data.get("decoding_parameters", {}).get(param_name, {})
    elif param_type == "preprocessing":
        param_info = doc_data.get("preprocessing_parameters", {}).get(param_name, {})
    else:
        return ""
    
    if not param_info:
        return ""
    
    # Create tooltip content
    tooltip_content = f"""
    <div style="position: relative; display: inline-block;">
        <span style="cursor: help; color: #0066cc;">ⓘ</span>
        <div style="visibility: hidden; position: absolute; z-index: 1; width: 300px; background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 5px; padding: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); left: 100%; top: 0;">
            <strong>{param_info.get('name', param_name)}</strong><br>
            {param_info.get('description', '')}<br><br>
            <strong>Use Cases:</strong><br>
            {', '.join(param_info.get('use_cases', []))}<br><br>
            <strong>Advantages:</strong><br>
            {', '.join(param_info.get('advantages', [])[:3])}...
        </div>
    </div>
    """
    
    return tooltip_content
