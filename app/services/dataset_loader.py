
from pathlib import Path
import pandas as pd


def load_dataset(dataset_source):
    """
    Load a dataset from a CSV/Excel file or an existing DataFrame.
    Returns a separate DataFrame without modifying the original.
    """

    if isinstance(dataset_source, pd.DataFrame):
        return dataset_source.copy(deep=True)

    file_path = Path(dataset_source)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)

    elif file_path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported dataset format. Use CSV or Excel."
        )

