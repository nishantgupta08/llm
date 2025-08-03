import streamlit as st
import pandas as pd

def model_picker_table(models_df, key="model_picker"):
    # The value of the radio is the index (row number) of the selected model
    model_names = [f"{row['name']} ({row['type']})" for _, row in models_df.iterrows()]
    selected_index = st.radio("Pick a model:", options=list(models_df.index), format_func=lambda i: model_names[i], key=key)

    # Table with a radio in the first column
    st.write("### Model Selection Table")
    cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
    headers = ["", "Name", "Type", "Size", "Trained On", "Source", "Description", "Intended Use"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")

    for i, row in models_df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2])
        # Show a radio button (looks like a bullet) in the first column
        with cols[0]:
            st.radio(
                label="",
                options=[i],  # Only this row's index
                index=0,
                key=f"radio_row_{i}",
                disabled=True,
            )
            # Use emoji to visually highlight the selected row
            if i == selected_index:
                st.markdown(":radio_button:", unsafe_allow_html=True)
        # Show data, highlight if selected
        highlight = "background-color: #E3F2FD;" if i == selected_index else ""
        for j, colname in enumerate(["name", "type", "size", "trained_on", "source", "description", "intended_use"], 1):
            cols[j].markdown(
                f"<div style='{highlight}'>{row[colname]}</div>", unsafe_allow_html=True
            )

    # Return the selected model (as Series)
    return models_df.loc[selected_index]

# Example usage
# models_df = pd.DataFrame(all_models)
# selected_model = model_picker_table(models_df)
