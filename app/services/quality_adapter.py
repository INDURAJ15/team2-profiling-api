
from app.services.dataset_loader import load_dataset
from app.services.team1_data_quality import DataQualityEngine


def check_data_quality(
    dataset_source="app/data/sample.csv",
    dataset_name="Dataset",
    target_col=None,
    id_cols=None
):
    # Load dataset
    df = load_dataset(dataset_source)

    # Run Team 1 Data Quality Engine
    engine = DataQualityEngine(
        df,
        dataset_name=dataset_name,
        target_col=target_col,
        id_cols=id_cols or ["employee_id"]
    )

    result_df = engine.run_checks()

    # Convert Team 1 findings into API response format
    issue_logs = []

    for _, row in result_df.iterrows():
        issue_logs.append({
            "issue_id": row["RuleID"],
            "category": row["Category"],
            "severity": row["Severity"],
            "affected_column": row["Column"],
            "affected_row_count": row["AffectedRows"],
            "description": row["Description"],
            "recommended_action": row["Recommendation"]
        })

    return {
        "status": "success",
        "validation_summary": {
            "total_issues_detected": len(issue_logs),
            "total_duplicate_records": sum(
                1 for issue in issue_logs
                if issue["category"] == "Duplicate Identifiers"
            ),
            "execution_mode": "non_destructive",
            "source_mutated": False
        },
        "issue_logs": issue_logs
    }
