"""
types.py

Shared type definitions for encoding and decoding strategies.
"""

from enum import Enum


class InputType(str, Enum):
    """UI control type for Streamlit sidebar."""
    SLIDER = "slider"
    NUMBER = "number_input"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"


class ValueType(str, Enum):
    """Data type of parameter value."""
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str" 