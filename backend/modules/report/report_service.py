from modules.report.repository import (
    get_patient_by_hash,
    get_patient_tests
)


def build_summary(pid_hash: str):

    patient = get_patient_by_hash(pid_hash)

    if not patient:
        return {"error": "Patient not found"}

    patient_id, name, age, gender = patient

    # (You can later improve abnormal logic here)
    status = "Ready"

    return {
        "patientName": name,
        "age": age,
        "gender": gender,
        "reportId": f"RPT-{patient_id}",
        "labRef": f"DL-{patient_id}",
        "status": status,
    }


def load_patient_context(patient_id: int):

    tests = get_patient_tests(patient_id)

    report_summary = ""

    for param, value in tests:
        if value:
            report_summary += f"{param}: {value}\n"

    return report_summary