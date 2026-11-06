# Team 2 – Profiling and Quality Regression Report

**Date:** 06-Nov-2026  
**Project:** Profiling and Quality Service Integration  
**Team:** Team 2 – Backend & AI/ML Integration  
**Repository:** https://github.com/INDURAJ15/team2-profiling-api  
**Branch:** main

## 1. Objective

Validate the integration of Data Profiling and Data Quality services, including:
- Numerical and categorical data profiling.
- Missing-value and duplicate detection.
- Mixed and unusual data type handling.
- Empty and partially valid dataset handling.
- Service exception handling.
- Orchestration and response consistency.

## 2. Test Results

| Test case | Expected / verified result | Status |
|---|---|---|
| Normal sample dataset | Profiling and Quality execute successfully | PASS |
| Numerical and categorical columns | Column types and statistics returned | PASS |
| Missing values | Missing age and salary findings detected | PASS |
| Duplicate identifiers | Duplicate identifier finding detected | PASS |
| Negative numeric values | Invalid negative value finding detected | PASS |
| Partial dataset | Mixed type warnings and missing-value finding returned | PASS |
| Unusual data types | Boolean detected; mixed score warning returned | PASS |
| Empty dataset | EMPTY_DATASET error returned | PASS |
| Missing file | SOURCE_NOT_FOUND error returned | PASS |
| Orchestration – normal dataset | Profiling and Quality both execute | PASS |
| Orchestration – unusual types | Profiling warning and Quality success returned | PASS |
| Orchestration – partial dataset | Profiling warnings and Quality findings returned | PASS |
| Source mutation | source_mutated reported as false in tested Quality responses | PASS |
| Python compilation | compileall completed without errors | PASS |
| Git whitespace validation | git diff --check completed without errors | PASS |

## 3. Detailed Observations

### Data Profiling
- Numerical and categorical columns are profiled.
- Missing counts, percentages, unique counts and other available statistics are returned.
- Boolean columns are identified as boolean.
- Mixed values in score, age and salary columns produce MIXED_TYPES warnings.
- The joining_date column containing an invalid date value was classified as categorical in the unusual-types test.

### Data Quality
- Missing values are reported with VAL_NULL_001.
- Duplicate identifiers are reported with VAL_DUP_001.
- Negative numeric values are reported with VAL_INV_001.
- Statistical outliers are reported with VAL_OUT_001.
- Empty datasets return EMPTY_DATASET.
- Missing files return SOURCE_NOT_FOUND.
- Tested Quality responses report non_destructive execution and source_mutated as false.

### Orchestration
- Profiling and Quality execute independently.
- A warning from Profiling does not prevent Quality execution.
- Overall status reflects the service results.
- Tested partial and unusual datasets returned HTTP 200.
- Semantic Analysis currently returns not_configured.

## 4. Known Issues and Pending Items

1. Mixed non-numeric values such as abc in age and invalid in salary are detected by Profiling as mixed types, but are not currently reported as Quality findings.
2. Team 1 confirmation is required on whether these values should be treated as Data Quality issues, including the expected rule ID and severity.
3. joining_date with an invalid value is currently classified as categorical rather than a date-specific type.
4. Semantic Analysis integration is pending because its API endpoint and agreed request/response contract are not yet available.
5. These observations require further review and should not be considered resolved defects.

## 5. Code and GitHub Update

- Updated file: app/services/quality_adapter.py
- Added empty dataset handling.
- Added handling for pandas EmptyDataError.
- Added safe error responses for missing files and unexpected exceptions.
- Regression checks passed for normal, empty and missing-file datasets.

**Commit:** 5151099  
**Commit message:** Handle empty datasets in quality adapter  
**Branch:** main  
**Push status:** Successfully pushed to origin/main.

## 6. Final Summary

The Team 2 Profiling and Data Quality services were tested using normal, partial, duplicate, invalid-value, empty and unusual-type datasets.

The orchestration endpoint successfully executed both services in the tested scenarios. Empty dataset and missing-file handling were validated. The latest Quality adapter change was committed and pushed to GitHub.

Mixed-value Quality validation and Semantic Analysis integration remain pending confirmation or external API contract availability.

**Report status:** Regression testing completed for the listed cases; pending integration items remain open.
