
import pandas as pd
from pathlib import Path
from app.services.dataset_loader import load_dataset


def profile_sample_dataset(dataset_source="app/data/sample.csv"):

    # 1. Load sample CSV dataset
    file_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "sample.csv"
    )

    df = load_dataset(dataset_source)

    # 2. Basic dataset information
    total_rows = len(df)
    total_columns = len(df.columns)

    # 3. Duplicate record count
    duplicate_count = int(df.duplicated().sum())

    # 4. Column-level profiling
    column_statistics = {}

    for column in df.columns:

        column_data = df[column]
        non_missing_data = column_data.dropna()

        column_info = {
            "data_type": str(column_data.dtype),
            "missing_count": int(column_data.isnull().sum()),
            "missing_percentage": round(
                float(column_data.isnull().mean() * 100), 2
            ),
            "unique_values": int(column_data.nunique())
        }

        # 5. Numerical column statistics
        if pd.api.types.is_numeric_dtype(column_data):

            column_info.update({
                "mean": (
                    float(non_missing_data.mean())
                    if not non_missing_data.empty else None
                ),
                "min": (
                    float(non_missing_data.min())
                    if not non_missing_data.empty else None
                ),
                "max": (
                    float(non_missing_data.max())
                    if not non_missing_data.empty else None
                ),
                "standard_deviation": (
                    float(non_missing_data.std())
                    if len(non_missing_data) > 1 else None
                ),
                "percentiles": (
                    {
                        "25%": float(non_missing_data.quantile(0.25)),
                        "50%": float(non_missing_data.quantile(0.50)),
                        "75%": float(non_missing_data.quantile(0.75))
                    }
                    if not non_missing_data.empty else None
                )
            })

        # 6. Categorical column statistics
        else:

            value_counts = column_data.value_counts().head(10)

            column_info["top_values"] = {
                str(value): int(count)
                for value, count in value_counts.items()
            }

        column_statistics[column] = column_info

    # 7. Final profiling response
    return {
        "status": "success",
        "total_rows": total_rows,
        "total_columns": total_columns,
        "duplicate_count": duplicate_count,
        "memory_usage_bytes": int(
            df.memory_usage(deep=True).sum()
        ),
        "profiling_metadata": column_statistics
    }
