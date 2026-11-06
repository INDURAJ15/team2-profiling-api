import json
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from main import app

schema_path = r"C:\Users\ASUS\Downloads\sample_profiling_request\profiling_response.schema.json"

with open(schema_path, "r", encoding="utf-8") as file:
    schema = json.load(file)

client = TestClient(app)

request_data = {
    "schema_version": "1.0-draft",
    "request_id": "test-001",
    "dataset_reference": {
        "dataset_id": "hr_employee",
        "source_type": "file",
        "location": r"C:\Users\ASUS\Downloads\HumanResources.Employee.xlsx"
    },
    "options": {
        "top_n_values": 5,
        "include_statistics": True,
        "include_correlations": True
    }
}

response = client.post("/api/v1/profiling/", json=request_data)

print("HTTP Status:", response.status_code)

if response.status_code == 200:
    response_data = response.json()

    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(response_data),
        key=lambda error: str(error.path)
    )

    if not errors:
        print("SUCCESS: API response matches Team 1 schema.")
    else:
        print("FAILED: Schema mismatches found:", len(errors))

        for error in errors:
            field = ".".join(str(item) for item in error.path)
            print(f"\nField: {field or 'root'}")
            print("Issue:", error.message)
else:
    print("API Error:", response.text)