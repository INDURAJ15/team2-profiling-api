import pandas as pd
import numpy as np


class DataQualityEngine:

    def __init__(self, df, dataset_name="Dataset",
                 target_col=None, id_cols=None):

        self.df = df.copy()
        self.dataset_name = dataset_name
        self.target_col = target_col
        self.id_cols = id_cols if id_cols else []
        self.issues = []

    def add_issue(self, rule_id, category, severity,
                  column, affected_count, description,
                  recommendation):

        self.issues.append({
            "Dataset": self.dataset_name,
            "RuleID": rule_id,
            "Category": category,
            "Severity": severity,
            "Column": column,
            "AffectedRows": int(affected_count),
            "Description": description,
            "Recommendation": recommendation
        })

    def run_checks(self):

        # Missing Value Checks
        for col in self.df.columns:

            missing_count = self.df[col].isnull().sum()

            if missing_count > 0:

                is_target = (col == self.target_col)

                severity = (
                    "Blocking Error" if is_target else "Warning"
                )

                category = (
                    "Missing Target" if is_target
                    else "Missing Values"
                )

                self.add_issue(
                    "VAL_NULL_001",
                    category,
                    severity,
                    col,
                    missing_count,
                    f"Column '{col}' contains {missing_count} missing values.",
                    "Apply imputation or drop rows if target is missing."
                )

        # Duplicate Identifier Checks
        for id_col in self.id_cols:

            if id_col in self.df.columns:

                dup_count = self.df[id_col].duplicated().sum()

                if dup_count > 0:

                    self.add_issue(
                        "VAL_DUP_001",
                        "Duplicate Identifiers",
                        "Blocking Error",
                        id_col,
                        dup_count,
                        f"Identifier column '{id_col}' contains {dup_count} duplicate entries.",
                        "Investigate primary key relationship or composite keys."
                    )

        # Numerical Validation and IQR Outliers
        num_cols = self.df.select_dtypes(
            include=[np.number]
        ).columns

        for col in num_cols:

            series = self.df[col].dropna()

            if len(series) == 0:
                continue

            invalid_mask = series < 0
            inv_count = invalid_mask.sum()

            if inv_count > 0:

                self.add_issue(
                    "VAL_INV_001",
                    "Confirmed Invalid Values",
                    "Blocking Error",
                    col,
                    inv_count,
                    f"Column '{col}' contains {inv_count} physically impossible negative values.",
                    "Correct data entry error or filter out."
                )

            series_valid = series[~invalid_mask]

            if len(series_valid) > 4:

                Q1 = series_valid.quantile(0.25)
                Q3 = series_valid.quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = series_valid[
                    (series_valid < lower_bound) |
                    (series_valid > upper_bound)
                ]

                if len(outliers) > 0:

                    self.add_issue(
                        "VAL_OUT_001",
                        "Statistical Outliers",
                        "Warning",
                        col,
                        len(outliers),
                        f"Column '{col}' has {len(outliers)} statistical outliers beyond IQR bounds.",
                        "Retain data; apply robust scaling or winsorization."
                    )

        return pd.DataFrame(self.issues)