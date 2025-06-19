import math
from typing import Any


def sanitize_float_values(data: Any) -> Any:
    """Recursively replace non JSON-compliant floats by ``None``.

    ``float('inf')``, ``float('-inf')`` and ``float('nan')`` values are not valid
    in JSON. This helper walks through lists and dictionaries to convert them to
    ``None`` so that FastAPI can safely serialize the result.
    """

    if isinstance(data, float):
        if math.isinf(data) or math.isnan(data):
            return None
        return data
    elif isinstance(data, list):
        return [sanitize_float_values(item) for item in data]
    elif isinstance(data, dict):
        return {key: sanitize_float_values(value) for key, value in data.items()}
    return data
