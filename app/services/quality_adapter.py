
import pandas as pd
from pathlib import Path
from app.services.dataset_loader import load_dataset


def check_data_quality(dataset_source="app/data/sample.csv"):

    # 1. Load sample dataset
    file_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "sample.csv"
    )

    df = load_dataset(dataset_source)

    # Keep original data unchanged
    original_df = df.copy(deep=True)

    issue_logs = []

    # 2. Missing value validation
    for column in df.columns:

        missing_count = int(df[column].isnull().sum())

        if missing_count > 0:
            missing_percentage = round(
                (missing_count / len(df)) * 100, 2
            )

            issue_logs.append({
                "issue_id": f"MISSING_{column.upper()}",
                "rule_id": "RULE_MISSING_VAL_01",
                "category": "Missing Values",
                "severity": "WARNING",
                "affected_column": column,
                "affected_row_count": missing_count,
                "description": (
                    f"{missing_count} missing values found "
                    f"({missing_percentage}%)"
                ),
                "recommended_action": (
                    "Review missing values and apply an "
                    "appropriate imputation or removal strategy."
                )
            })

    # 3. Duplicate record validation
    duplicate_count = int(df.duplicated().sum())

    if duplicate_count > 0:
        issue_logs.append({
            "issue_id": "DUPLICATE_RECORDS",
            "rule_id": "RULE_DUPLICATE_01",
            "category": "Duplicate Records",
            "severity": "WARNING",
            "affected_column": "all",
            "affected_row_count": duplicate_count,
            "description": (
                f"{duplicate_count} duplicate records found"
            ),
            "recommended_action": (
                "Review duplicate records before removing them."
            )
        })

    # 4. Invalid age validation
    if "age" in df.columns:

        invalid_age_mask = (
            (df["age"] < 18) | (df["age"] > 100)
        )

        invalid_age_count = int(invalid_age_mask.sum())

        if invalid_age_count > 0:
            issue_logs.append({
                "issue_id": "INVALID_AGE",
                "rule_id": "RULE_AGE_RANGE_01",
                "category": "Numerical Range",
                "severity": "ERROR",
                "affected_column": "age",
                "affected_row_count": invalid_age_count,
                "description": (
                    f"{invalid_age_count} age values are outside "
                    "the allowed range 18-100"
                ),
                "recommended_action": (
                    "Verify age values and correct invalid entries."
                )
            })

    # 5. Verify source data is unchanged
    source_mutated = not df.equals(original_df)

    # 6. Final quality response
    return {
        "status": "success",
        "validation_summary": {
            "total_issues_detected": len(issue_logs),
            "total_duplicate_records": duplicate_count,
            "execution_mode": "non_destructive",
            "source_mutated": source_mutated
        },
        "issue_logs": issue_logs
    }
