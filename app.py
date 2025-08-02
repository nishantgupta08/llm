from utils.ui_utils import parameter_table
from config.tasks import get_ideal_value, get_ideal_value_reason

# Example usage:
param_values = parameter_table(
    param_dict=get_task_parameters(task_choice),
    task_name=task_choice,
    param_category="parameters",
    get_ideal_value=get_ideal_value,
    get_ideal_value_reason=get_ideal_value_reason
)
