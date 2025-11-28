import json
from backend.orchestrator.orchestrator import build_orchestrator_graph

if __name__ == "__main__":
    graph = build_orchestrator_graph()

    # Test Case 1: Chest pain (possible cardiac issue)
    print("\n" + "="*80)
    print("TEST CASE 1: Chest Pain")
    print("="*80)
    input_state_1 = {
        "symptoms": "chest pain, shortness of breath, sweating",
        "age": 55,
        "gender": "male",
        "history": "hypertension, smoking 20 years",
        "currentMedications": "lisinopril",
        "urgency": "high"
    }
    
    final_state_1 = graph.invoke(input_state_1)
    print(f"\n✅ Diagnosis: {final_state_1.get('diagnosis', 'N/A')}")
    print(f"📚 Literature: {len(final_state_1.get('literature', {}).get('articles', {}).get('summaries', []))} articles")
    print(f"🔍 Case Matches: {len(final_state_1.get('case_matcher', {}).get('matched_cases', []))} matches")
    print(f"💊 Treatments: {len(final_state_1.get('treatment', {}).get('treatments', []))} treatments")
    
    # Test Case 2: Headache (neurological)
    print("\n" + "="*80)
    print("TEST CASE 2: Severe Headache")
    print("="*80)
    input_state_2 = {
        "symptoms": "severe headache, nausea, sensitivity to light",
        "age": 32,
        "gender": "female",
        "history": "migraines since age 20",
        "urgency": "medium"
    }
    
    final_state_2 = graph.invoke(input_state_2)
    print(f"\n✅ Diagnosis: {final_state_2.get('diagnosis', 'N/A')}")
    print(f"📚 Literature: {len(final_state_2.get('literature', {}).get('articles', {}).get('summaries', []))} articles")
    print(f"🔍 Case Matches: {len(final_state_2.get('case_matcher', {}).get('matched_cases', []))} matches")
    print(f"💊 Treatments: {len(final_state_2.get('treatment', {}).get('treatments', []))} treatments")
    
    # Test Case 3: Joint pain (rheumatological)
    print("\n" + "="*80)
    print("TEST CASE 3: Joint Pain")
    print("="*80)
    input_state_3 = {
        "symptoms": "joint pain in hands and knees, morning stiffness, swelling",
        "age": 48,
        "gender": "female",
        "history": "no significant medical history",
        "urgency": "low"
    }
    
    final_state_3 = graph.invoke(input_state_3)
    print(f"\n✅ Diagnosis: {final_state_3.get('diagnosis', 'N/A')}")
    print(f"📚 Literature: {len(final_state_3.get('literature', {}).get('articles', {}).get('summaries', []))} articles")
    print(f"🔍 Case Matches: {len(final_state_3.get('case_matcher', {}).get('matched_cases', []))} matches")
    print(f"💊 Treatments: {len(final_state_3.get('treatment', {}).get('treatments', []))} treatments")
    
    print("\n" + "="*80)
    print("✅ ALL CUSTOM CASES COMPLETED!")
    print("="*80)
