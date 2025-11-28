"""
Test PDF generation with complete patient data
"""
from backend.utils.pdf_generator import generate_pdf_from_analysis

# Complete test data matching frontend structure
test_data = {
    "patient_info": {
        "patientId": "jif",
        "age": 65,
        "gender": "Male",
        "urgency": "high",
        "medicalHistory": "Hypertension, Type 2 Diabetes",
        "currentMedications": ["sporidex", "metformin", "lisinopril"],
        "primary_complaint": "Severe chest pain radiating to left arm, shortness of breath, and sweating for the past 2 hours"
    },
    "symptom_analysis": {
        "risk_level": "high",
        "top_differentials": [
            {
                "name": "Acute Myocardial Infarction",
                "icd10cm_code": "I21.9",
                "rationale": "Classic presentation of chest pain with radiation, shortness of breath, and diaphoresis in a patient with cardiac risk factors"
            },
            {
                "name": "Unstable Angina",
                "icd10cm_code": "I20.0",
                "rationale": "Alternative diagnosis - ischemic chest pain without elevated cardiac markers"
            },
            {
                "name": "Acute Coronary Syndrome",
                "icd10cm_code": "I24.9",
                "rationale": "Umbrella diagnosis for acute cardiac ischemic events"
            }
        ]
    },
    "treatment": {
        "treatments": [
            {
                "type": "drug",
                "name": "Aspirin",
                "class": "Antiplatelet",
                "rationale": "Immediate platelet inhibition to prevent thrombus formation",
                "source": "RxNorm API"
            },
            {
                "type": "drug",
                "name": "Nitroglycerin",
                "class": "Vasodilator",
                "rationale": "Coronary vasodilation to improve myocardial oxygen supply",
                "source": "RxNorm API"
            },
            {
                "type": "drug",
                "name": "Morphine",
                "class": "Opioid Analgesic",
                "rationale": "Pain management and anxiety reduction",
                "source": "Clinical Guidelines"
            },
            {
                "type": "non-drug",
                "name": "Immediate Emergency Care",
                "rationale": "Call 911 immediately for suspected acute myocardial infarction"
            },
            {
                "type": "non-drug",
                "name": "Cardiac Monitoring",
                "rationale": "Continuous ECG monitoring for arrhythmia detection"
            }
        ]
    },
    "literature": {
        "articles": {
            "summaries": [
                {
                    "title": "2021 ACC/AHA Guidelines for Acute Myocardial Infarction Management",
                    "pmid": "34755492",
                    "summary": "Comprehensive evidence-based guidelines for diagnosis and treatment of acute MI, including immediate antiplatelet therapy and reperfusion strategies"
                },
                {
                    "title": "Early Recognition and Treatment of Acute Coronary Syndromes",
                    "pmid": "33142034",
                    "summary": "Review of clinical presentation, diagnostic criteria, and time-sensitive interventions for ACS"
                },
                {
                    "title": "Risk Stratification in Patients with Chest Pain",
                    "pmid": "32845678",
                    "summary": "Evidence-based approach to differentiating cardiac from non-cardiac chest pain in emergency settings"
                }
            ]
        }
    },
    "case_matcher": {
        "matched_cases": [
            {
                "name": "Myocardial Infarction",
                "icd_code": "I21.9",
                "description": "Acute ST-elevation myocardial infarction with classic presentation",
                "match_score": 95
            },
            {
                "name": "Unstable Angina Pectoris",
                "icd_code": "I20.0",
                "description": "Acute coronary syndrome without elevated cardiac biomarkers",
                "match_score": 88
            },
            {
                "name": "Acute Coronary Syndrome",
                "icd_code": "I24.9",
                "description": "Acute ischemic heart disease requiring urgent intervention",
                "match_score": 92
            }
        ]
    },
    "summary": {
        "patient_summary": "65-year-old male with history of hypertension and type 2 diabetes presenting with acute onset severe chest pain, left arm radiation, shortness of breath, and diaphoresis",
        "clinical_summary": "High clinical suspicion for acute myocardial infarction based on classic presentation and risk factor profile. Immediate emergency intervention required with aspirin, nitroglycerin, and cardiac monitoring. Urgent cardiology consultation and possible catheterization indicated.",
        "recommendations": [
            {"type": "next_steps", "content": "IMMEDIATE 911 call for emergency transport to cardiac-capable facility"},
            {"type": "next_steps", "content": "12-lead ECG within 10 minutes of presentation"},
            {"type": "next_steps", "content": "Serial troponin measurements at 0, 3, and 6 hours"},
            {"type": "next_steps", "content": "Cardiology consultation for possible cardiac catheterization"},
            {"type": "next_steps", "content": "Continuous cardiac monitoring and vital sign surveillance"}
        ]
    }
}

try:
    print("🔄 Generating complete PDF with patient data...")
    pdf_bytes = generate_pdf_from_analysis(test_data)
    print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
    
    # Save to file
    with open("test_complete_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ PDF saved as test_complete_report.pdf")
    print("\n📋 Patient Info Included:")
    print(f"  - Patient ID: {test_data['patient_info']['patientId']}")
    print(f"  - Age: {test_data['patient_info']['age']}")
    print(f"  - Medications: {', '.join(test_data['patient_info']['currentMedications'])}")
    print(f"  - Chief Complaint: {test_data['patient_info']['primary_complaint'][:50]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
