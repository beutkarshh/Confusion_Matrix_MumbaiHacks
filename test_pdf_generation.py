"""
Quick test to verify PDF generation works
"""
from backend.utils.pdf_generator import generate_pdf_from_analysis

# Minimal test data
test_data = {
    "patient_info": {
        "patientId": "TEST001",
        "age": 45,
        "gender": "Male",
        "urgency": "routine",
        "medicalHistory": "Type 2 Diabetes",
        "currentMedications": ["Metformin 500mg"],
        "primary_complaint": "Frequent urination and increased thirst"
    },
    "symptom_analysis": {
        "risk_level": "medium",
        "top_differentials": [
            {
                "name": "Type 2 Diabetes Mellitus",
                "icd10cm_code": "E11.9",
                "rationale": "Classic symptoms of polyuria and polydipsia with known diabetes history"
            }
        ]
    },
    "treatment": {
        "treatments": [
            {
                "type": "drug",
                "name": "Metformin",
                "class": "Biguanide",
                "rationale": "First-line therapy for Type 2 Diabetes"
            },
            {
                "type": "non-drug",
                "name": "Dietary modification",
                "rationale": "Low carbohydrate diet to manage blood glucose"
            }
        ]
    },
    "literature": {
        "articles": {
            "summaries": [
                {
                    "title": "Management of Type 2 Diabetes",
                    "pmid": "12345678",
                    "summary": "Evidence-based guidelines for diabetes management"
                }
            ]
        }
    },
    "summary": {
        "patient_summary": "45-year-old male with Type 2 Diabetes presenting with classic symptoms",
        "clinical_summary": "Patient requires glycemic control optimization",
        "recommendations": [
            {"type": "next_steps", "content": "Check HbA1c and fasting glucose"}
        ]
    }
}

try:
    print("🔄 Generating PDF...")
    pdf_bytes = generate_pdf_from_analysis(test_data)
    print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
    
    # Save to file for verification
    with open("test_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ PDF saved as test_report.pdf")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
