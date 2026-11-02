import pandas as pd
from pathlib import Path


def profile_sample_dataset():

    # Load sample CSV dataset
    file_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "sample.csv"
    )

    df = pd.read_csv(file_path)

    # Basic dataset information
    total_rows = len(df)
    total_columns = len(df.columns)

    # Column profiling
    column_statistics = {}

    for column in df.columns:

        column_data = df[column]

        column_statistics[column] = {
            "data_type": str(column_data.dtype),
            "missing_count": int(column_data.isnull().sum()),
            "missing_percentage": round(
                float(column_data.isnull().mean() * 100), 2
            ),
            "unique_values": int(column_data.nunique()),
        }

        # Numeric column statistics
        if pd.api.types.is_numeric_dtype(column_data):

            column_statistics[column].update({
                "mean": (
                    float(column_data.mean())
                    if not column_data.dropna().empty
                    else None
                ),
                "min": (
                    float(column_data.min())
                    if not column_data.dropna().empty
                    else None
                ),
                "max": (
                    float(column_data.max())
                    if not column_data.dropna().empty
                    else None
                )
            })

    return {
        "status": "success",
        "total_rows": total_rows,
        "total_columns": total_columns,
        "memory_usage_bytes": int(
            df.memory_usage(deep=True).sum()
        ),
        "profiling_metadata": column_statistics
    }