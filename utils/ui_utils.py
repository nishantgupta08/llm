import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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

    param_values = {}
    for name, cfg in param_dict.items():
        row_cols = st.columns(WIDTHS)
        with row_cols[0]: st.markdown(cfg.get("label", name))
        with row_cols[1]: st.markdown(cfg.get("info", ""))
        with row_cols[2]: st.markdown(str(cfg.get("ideal_value_reason", "")))

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
                step = int(cfg.get("step", 1))
                try:
                    val = int(st.session_state[val_key])
                except Exception:
                    val = minv
                value = c_val.slider(
                    "", min_value=minv, max_value=maxv, value=val, step=step, key=val_key, label_visibility="collapsed"
                )
            elif typ == "checkbox":
                value = c


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
