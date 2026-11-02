import pandas as pd
from pathlib import Path


def check_data_quality():

    file_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "sample.csv"
    )

    df = pd.read_csv(file_path)

    issue_logs = []

    # 1. Missing value check
    for column in df.columns:
        missing_count = int(df[column].isnull().sum())

        if missing_count > 0:
            issue_logs.append({
                "rule_id": "RULE_MISSING_VAL_01",
                "category": "Missing Values",
                "severity": "WARNING",
                "affected_column": column,
                "affected_row_count": missing_count,
                "description": f"{missing_count} missing values found"
            })

    # 2. Duplicate check
    duplicate_count = int(df.duplicated().sum())

    if duplicate_count > 0:
        issue_logs.append({
            "rule_id": "RULE_DUPLICATE_01",
            "category": "Duplicate Records",
            "severity": "WARNING",
            "affected_column": "all",
            "affected_row_count": duplicate_count,
            "description": "Duplicate records found"
        })

    # 3. Age range check
    if "age" in df.columns:
        invalid_age = int(
            ((df["age"] < 18) | (df["age"] > 100)).sum()
        )

        if invalid_age > 0:
            issue_logs.append({
                "rule_id": "RULE_AGE_RANGE_01",
                "category": "Numerical Range",
                "severity": "ERROR",
                "affected_column": "age",
                "affected_row_count": invalid_age,
                "description": "Age values outside the allowed range 18-100"
            })

    return {
        "status": "success",
        "validation_summary": {
            "total_issues_detected": len(issue_logs),
            "execution_mode": "non_destructive",
            "source_mutated": False
        },
        "issue_logs": issue_logs
    }