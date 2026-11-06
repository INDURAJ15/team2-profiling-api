
import pandas as pd
import numpy as np

from datetime import datetime, timezone
from time import perf_counter

from app.services.dataset_loader import load_dataset


def make_error(code, message, field=None):
    return {
        "code": code,
        "message": message,
        "field": field
    }


def make_warning(code, severity, column, message):
    return {
        "code": code,
        "severity": severity,
        "column": column,
        "message": message
    }


def infer_type(series):
    values = series.dropna()

    if values.empty:
        return "empty"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numerical"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    converted = pd.to_numeric(values, errors="coerce")

    if converted.notna().all():
        return "numerical"

    if converted.notna().any():
        return "mixed"

    dates = pd.to_datetime(values, errors="coerce")

    if dates.notna().all():
        return "datetime"

    if values.nunique() <= 20:
        return "categorical"

    return "text"


def profile_sample_dataset(
    dataset_source,
    dataset_id,
    request_id=None,
    options=None,
    metadata=None
):
    start_time = perf_counter()

    options = options or {}
    metadata = metadata or {}

    top_n = options.get("top_n_values", 5)
    include_statistics = options.get("include_statistics", True)
    include_correlations = options.get("include_correlations", True)
    target_column = options.get("target_column")

    identifier_columns = metadata.get("identifier_columns", [])
    missing_markers = metadata.get("missing_value_markers", [])

    dataset_reference = {
        "dataset_id": dataset_id,
        "name": metadata.get("name")
    }

    warnings = []
    errors = []

    def build_response(
        status,
        dataset=None,
        columns=None,
        correlations=None,
        class_distribution=None
    ):
        result = {
            "schema_version": "1.0-draft",
            "request_id": request_id,
            "module": "dataset_profiling",
            "status": status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round(
                (perf_counter() - start_time) * 1000, 2
            ),
            "dataset_reference": dataset_reference,
            "dataset": dataset,
            "columns": columns if columns is not None else [],
            "warnings": warnings,
            "errors": errors
        }

        if correlations is not None:
            result["correlations"] = correlations

        if class_distribution is not None:
            result["class_distribution"] = class_distribution

        return result

    # 1. Load dataset

    try:
        df = load_dataset(dataset_source)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Dataset is not a valid table.")

    except FileNotFoundError:
        errors.append(make_error(
            "SOURCE_NOT_FOUND",
            "The requested dataset source was not found.",
            "dataset_reference"
        ))
        return build_response("failed")

    except Exception:
        errors.append(make_error(
            "DATASET_LOAD_FAILED",
            "Unable to load the requested dataset.",
            "dataset_reference"
        ))
        return build_response("failed")

    # 2. Check duplicate column names

    if df.columns.duplicated().any():
        errors.append(make_error(
            "DUPLICATE_COLUMN_NAMES",
            "The dataset contains duplicate column names.",
            "dataset"
        ))
        return build_response("failed")

    # 3. Missing value markers

    if missing_markers:
        df = df.replace(missing_markers, np.nan)

    row_count = int(df.shape[0])
    column_count = int(df.shape[1])
    duplicate_count = int(df.duplicated().sum())

    dataset_info = {
        "row_count": row_count,
        "column_count": column_count,
        "column_names": [str(c) for c in df.columns],
        "duplicate_row_count": duplicate_count
    }

    if row_count == 0:
        warnings.append(make_warning(
            "EMPTY_DATASET",
            "warning",
            None,
            "The dataset contains no rows."
        ))

    if duplicate_count > 0:
        warnings.append(make_warning(
            "DUPLICATES_APPROXIMATE",
            "info",
            None,
            f"The dataset contains {duplicate_count} duplicate rows."
        ))

    # 4. Profile columns

    columns = []
    numeric_columns = []

    for position, column_name in enumerate(df.columns):

        series = df[column_name]
        name = str(column_name)

        missing_count = int(series.isna().sum())
        missing_pct = (
            round(missing_count / row_count * 100, 2)
            if row_count else 0.0
        )

        unique_count = int(series.nunique(dropna=True))
        inferred_type = infer_type(series)

        likely_identifier = (
            name in identifier_columns
            or (
                row_count > 1
                and unique_count == row_count
                and missing_count == 0
            )
        )

        column_warnings = []

        if inferred_type == "empty":
            column_warnings.append("EMPTY_COLUMN")
            warnings.append(make_warning(
                "EMPTY_COLUMN", "warning", name,
                f"Column '{name}' contains only missing values."
            ))

        elif unique_count == 1:
            column_warnings.append("CONSTANT_COLUMN")
            warnings.append(make_warning(
                "CONSTANT_COLUMN", "info", name,
                f"Column '{name}' contains only one unique value."
            ))

        if (
            row_count > 0
            and unique_count / row_count > 0.9
            and not likely_identifier
        ):
            column_warnings.append("HIGH_CARDINALITY")
            warnings.append(make_warning(
                "HIGH_CARDINALITY", "info", name,
                f"Column '{name}' has high cardinality."
            ))

        if inferred_type == "mixed":
            column_warnings.append("MIXED_TYPES")
            warnings.append(make_warning(
                "MIXED_TYPES", "warning", name,
                f"Column '{name}' contains mixed data types."
            ))

        info = {
            "name": name,
            "position": position,
            "dtype": str(series.dtype),
            "inferred_type": inferred_type,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": unique_count,
            "likely_identifier": bool(likely_identifier),
            "warnings": column_warnings
        }

        values = series.dropna()

        # Numerical columns

        if inferred_type == "numerical":

            numeric = pd.to_numeric(series, errors="coerce").dropna()

            if not likely_identifier and not numeric.empty:
                numeric_columns.append(name)

            if (
                include_statistics
                and not likely_identifier
                and len(numeric) > 0
            ):
                info["summary"] = {
                    "min": float(numeric.min()),
                    "max": float(numeric.max()),
                    "mean": float(numeric.mean()),
                    "median": float(numeric.median()),
                    "std": float(numeric.std()) if len(numeric) > 1 else 0.0,
                    "q1": float(numeric.quantile(0.25)),
                    "q3": float(numeric.quantile(0.75)),
                    "skewness": float(numeric.skew()) if len(numeric) > 2 and np.isfinite(numeric.skew()) else 0.0
                }

                if numeric.nunique() > 1:
                    counts, edges = np.histogram(numeric, bins=10)

                    info["histogram"] = [
                        {
                            "start": float(edges[i]),
                            "end": float(edges[i + 1]),
                            "count": int(counts[i])
                        }
                        for i in range(len(counts))
                    ]

        # Datetime columns

        elif inferred_type == "datetime":

            if include_statistics and not values.empty:
                dates = pd.to_datetime(values, errors="coerce").dropna()

                if not dates.empty:
                    info["summary"] = {
                        "min": dates.min().isoformat(),
                        "max": dates.max().isoformat()
                    }

        # Text, categorical and boolean columns

        elif inferred_type in ["text", "categorical", "boolean"]:

            if include_statistics and not values.empty:
                lengths = values.astype(str).str.len()

                if inferred_type == "text":
                    info["summary"] = {
                        "avg_length": float(lengths.mean()),
                        "max_length": int(lengths.max())
                    }

            if not values.empty:
                counts = values.astype(str).value_counts().head(top_n)
                total = len(values)

                info["top_values"] = [
                    {
                        "value": str(value),
                        "count": int(count),
                        "percentage": round(int(count) / total * 100, 2)
                    }
                    for value, count in counts.items()
                ]

        columns.append(info)

    # 5. Correlations

    correlations = None

    if include_correlations and len(numeric_columns) >= 2:

        numeric_df = df[numeric_columns].apply(
            pd.to_numeric, errors="coerce"
        )

        matrix = numeric_df.corr(method="pearson")
        correlations = []

        for i, col_a in enumerate(numeric_columns):
            for col_b in numeric_columns[i + 1:]:

                value = matrix.loc[col_a, col_b]

                if pd.notna(value):
                    correlations.append({
                        "column_a": col_a,
                        "column_b": col_b,
                        "coefficient": round(float(value), 6)
                    })

        correlations.sort(
            key=lambda item: abs(item["coefficient"]),
            reverse=True
        )

    # 6. Target class distribution

    class_distribution = None

    if target_column:

        if target_column not in df.columns:
            errors.append(make_error(
                "TARGET_NOT_FOUND",
                "The requested target column was not found.",
                "options.target_column"
            ))
            return build_response("failed")

        target = df[target_column]
        target_values = target.dropna()
        counts = target_values.value_counts()

        if 1 <= len(counts) <= 20:

            total = int(len(target_values))
            minimum = int(counts.min())
            maximum = int(counts.max())

            class_distribution = {
                "target_column": str(target_column),
                "class_count": int(len(counts)),
                "classes": [
                    {
                        "value": str(value),
                        "count": int(count),
                        "percentage": round(int(count) / total * 100, 2)
                    }
                    for value, count in counts.items()
                ],
                "majority_class": str(counts.index[0]),
                "minority_class": str(counts.index[-1]),
                "imbalance_ratio": round(maximum / minimum, 4),
                "missing_count": int(target.isna().sum())
            }

        else:
            warnings.append(make_warning(
                "CLASS_DISTRIBUTION_SKIPPED",
                "info",
                str(target_column),
                "Class distribution was skipped because the target has no values or more than 20 distinct classes."
            ))

    # 7. Final response

    status = "warning" if warnings else "success"

    return build_response(
        status,
        dataset=dataset_info,
        columns=columns,
        correlations=correlations,
        class_distribution=class_distribution
    )
