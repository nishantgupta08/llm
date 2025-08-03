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
