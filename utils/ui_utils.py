import streamlit as st

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
    cols = st.columns([2, 3, 2, 2, 3])  # Adjust column width as needed
    headers = ["Label", "Info", "Ideal Value", "Reason", "Value"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    values = {}
    for p, cfg in param_dict.items():
        with cols[0]: st.markdown(cfg.get("label", p))
        with cols[1]: st.markdown(cfg.get("info", ""))
        ideal = get_ideal_value(task_name, param_category, p)
        reason = get_ideal_value_reason(task_name, param_category, p)
        with cols[2]: st.markdown(str(ideal) if ideal is not None else "")
        with cols[3]: st.markdown(str(reason) if reason is not None else "")
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
    return values
