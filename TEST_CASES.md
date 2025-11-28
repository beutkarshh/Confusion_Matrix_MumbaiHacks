# Medical AI System - Test Cases

## Test Case 1: Type 2 Diabetes (High Urgency)
**Patient Profile:**
- Age: 45
- Gender: Male
- Symptoms: increased thirst, frequent urination, unexplained weight loss, fatigue
- Medical History: family history of type 2 diabetes, obesity
- Current Medications: none
- Urgency: high

**Expected Results:**
- Diagnosis: Type 2 Diabetes Mellitus (ICD-10: E11)
- Tests: Fasting Blood Glucose, HbA1c, Gastric Emptying Study
- Treatment: Metformin, dietary modifications, exercise
- Confidence: ~85%

---

## Test Case 2: Acute Myocardial Infarction (Critical)
**Patient Profile:**
- Age: 58
- Gender: Male
- Symptoms: severe chest pain, shortness of breath, sweating, nausea, left arm pain
- Medical History: hypertension, high cholesterol, smoking for 25 years
- Current Medications: lisinopril, atorvastatin
- Urgency: critical

**Expected Results:**
- Diagnosis: Acute Myocardial Infarction (Heart Attack)
- Tests: ECG, Cardiac Troponin, Chest X-Ray, Echocardiogram
- Treatment: Aspirin, nitroglycerin, immediate hospital admission
- Confidence: ~90%

---

## Test Case 3: Migraine (Medium Urgency)
**Patient Profile:**
- Age: 32
- Gender: Female
- Symptoms: severe headache, nausea, sensitivity to light, visual disturbances
- Medical History: migraines since age 20, family history of migraines
- Current Medications: ibuprofen (as needed)
- Urgency: medium

**Expected Results:**
- Diagnosis: Migraine with Aura
- Tests: Neurological exam, CT/MRI if first occurrence
- Treatment: Sumatriptan, lifestyle modifications, trigger avoidance
- Confidence: ~80%

---

## Test Case 4: Rheumatoid Arthritis (Low Urgency)
**Patient Profile:**
- Age: 48
- Gender: Female
- Symptoms: joint pain in hands and knees, morning stiffness lasting over 1 hour, swelling in multiple joints
- Medical History: no significant medical history
- Current Medications: none
- Urgency: low

**Expected Results:**
- Diagnosis: Rheumatoid Arthritis
- Tests: Rheumatoid Factor (RF), Anti-CCP antibodies, ESR, CRP, X-rays
- Treatment: Methotrexate, NSAIDs, physical therapy
- Confidence: ~75%

---

## Test Case 5: Pneumonia (High Urgency)
**Patient Profile:**
- Age: 67
- Gender: Male
- Symptoms: high fever, persistent cough with yellow-green mucus, difficulty breathing, chest pain when breathing
- Medical History: COPD, former smoker
- Current Medications: albuterol inhaler
- Urgency: high

**Expected Results:**
- Diagnosis: Community-Acquired Pneumonia
- Tests: Chest X-Ray, Sputum culture, CBC, Oxygen saturation
- Treatment: Antibiotics (azithromycin/amoxicillin), oxygen therapy
- Confidence: ~85%

---

## Test Case 6: Hypothyroidism (Low Urgency)
**Patient Profile:**
- Age: 42
- Gender: Female
- Symptoms: fatigue, weight gain, cold intolerance, dry skin, constipation, depression
- Medical History: family history of thyroid disease
- Current Medications: none
- Urgency: low

**Expected Results:**
- Diagnosis: Hypothyroidism
- Tests: TSH, Free T4, Anti-TPO antibodies
- Treatment: Levothyroxine, regular monitoring
- Confidence: ~80%

---

## Test Case 7: Urinary Tract Infection (Medium Urgency)
**Patient Profile:**
- Age: 35
- Gender: Female
- Symptoms: burning sensation during urination, frequent urination, lower abdominal pain, cloudy urine
- Medical History: history of 2 previous UTIs
- Current Medications: none
- Urgency: medium

**Expected Results:**
- Diagnosis: Urinary Tract Infection (UTI)
- Tests: Urinalysis, Urine culture
- Treatment: Antibiotics (nitrofurantoin/trimethoprim), increased fluid intake
- Confidence: ~85%

---

## Test Case 8: Gastroesophageal Reflux Disease (Low Urgency)
**Patient Profile:**
- Age: 50
- Gender: Male
- Symptoms: heartburn after meals, regurgitation, difficulty swallowing, chest discomfort
- Medical History: obesity, hiatal hernia
- Current Medications: antacids (occasional)
- Urgency: low

**Expected Results:**
- Diagnosis: GERD (Gastroesophageal Reflux Disease)
- Tests: Upper endoscopy, pH monitoring, barium swallow
- Treatment: Proton pump inhibitors (omeprazole), dietary changes, weight loss
- Confidence: ~75%

---

## Test Case 9: Asthma Exacerbation (High Urgency)
**Patient Profile:**
- Age: 28
- Gender: Female
- Symptoms: wheezing, shortness of breath, chest tightness, persistent cough
- Medical History: asthma since childhood, seasonal allergies
- Current Medications: albuterol inhaler, fluticasone inhaler
- Urgency: high

**Expected Results:**
- Diagnosis: Asthma Exacerbation
- Tests: Peak flow measurement, Spirometry, Chest X-Ray
- Treatment: Nebulizer treatment, oral corticosteroids, increase inhaler use
- Confidence: ~85%

---

## Test Case 10: Anemia (Iron Deficiency) (Medium Urgency)
**Patient Profile:**
- Age: 38
- Gender: Female
- Symptoms: fatigue, weakness, pale skin, shortness of breath, dizziness, cold hands and feet
- Medical History: heavy menstrual periods, vegetarian diet
- Current Medications: none
- Urgency: medium

**Expected Results:**
- Diagnosis: Iron Deficiency Anemia
- Tests: CBC, Serum ferritin, Iron studies, TIBC
- Treatment: Iron supplements, dietary counseling, investigate cause
- Confidence: ~80%

---

## Test Case 11: Diabetic Gastroparesis (Medium Urgency)
**Patient Profile:**
- Age: 28
- Gender: Female
- Symptoms: nausea, vomiting, feeling full quickly, bloating, abdominal pain
- Medical History: Type 1 diabetes for 10 years, poor glucose control
- Current Medications: insulin
- Urgency: medium

**Expected Results:**
- Diagnosis: Diabetic Gastroparesis
- Tests: Gastric emptying study, Upper endoscopy, Blood glucose monitoring
- Treatment: Metoclopramide, dietary changes (small frequent meals), glucose control
- Confidence: ~75%

---

## Test Case 12: Hypertensive Crisis (Critical)
**Patient Profile:**
- Age: 62
- Gender: Male
- Symptoms: severe headache, blurred vision, chest pain, confusion, blood pressure 200/120
- Medical History: hypertension (poorly controlled), diabetes
- Current Medications: amlodipine (not taken regularly)
- Urgency: critical

**Expected Results:**
- Diagnosis: Hypertensive Crisis
- Tests: Blood pressure monitoring, ECG, Chest X-Ray, Renal function tests
- Treatment: IV antihypertensives, immediate hospitalization, medication adjustment
- Confidence: ~95%

---

## Edge Cases & Special Scenarios

### Test Case 13: Minimal Information
**Patient Profile:**
- Age: 30
- Gender: Female
- Symptoms: headache
- Medical History: none
- Current Medications: none
- Urgency: low

**Purpose:** Test how system handles vague symptoms

---

### Test Case 14: Multiple Chronic Conditions
**Patient Profile:**
- Age: 75
- Gender: Male
- Symptoms: fatigue, confusion, difficulty breathing
- Medical History: diabetes, heart failure, COPD, chronic kidney disease
- Current Medications: metformin, furosemide, albuterol, atorvastatin, aspirin
- Urgency: high

**Purpose:** Test complex multi-morbidity analysis

---

### Test Case 15: Pediatric Case
**Patient Profile:**
- Age: 8
- Gender: Male
- Symptoms: fever, sore throat, difficulty swallowing, swollen lymph nodes
- Medical History: none
- Current Medications: none
- Urgency: medium

**Expected Results:**
- Diagnosis: Strep Throat (Pharyngitis)
- Tests: Rapid strep test, Throat culture
- Treatment: Antibiotics (amoxicillin), pain relief
- Confidence: ~80%

---

## Testing Checklist

### Functional Testing
- [ ] All 15 test cases run successfully
- [ ] Diagnosis accuracy is reasonable
- [ ] ICD-10 codes are assigned correctly
- [ ] Literature search returns relevant articles
- [ ] Case matching finds similar conditions
- [ ] Treatment recommendations are appropriate
- [ ] PDF generation works for all cases

### Performance Testing
- [ ] Analysis completes within 3 minutes
- [ ] No timeout errors
- [ ] Progress bar updates smoothly
- [ ] Stats increment correctly

### UI Testing
- [ ] All agent status indicators update correctly
- [ ] Results display properly formatted
- [ ] PDF downloads successfully
- [ ] Dashboard stats show real numbers
- [ ] Login/logout works properly

### Edge Cases
- [ ] System handles missing fields gracefully
- [ ] System handles very long symptom descriptions
- [ ] System handles special characters
- [ ] System handles pediatric ages
- [ ] System handles geriatric ages (80+)

---

## Quick Test Commands

### Test Individual Agents:
```bash
# Symptom Analyzer
python backend/test_symptom.py

# Literature Agent
python backend/test_literature.py

# Case Matcher
python backend/test_case_matcher.py

# Treatment Agent
python backend/test_treatment.py

# Orchestrator (Full Flow)
python backend/test_orchestrator.py
```

### Test Multiple Cases:
```bash
python test_custom_cases.py
```

### Test Frontend:
1. Navigate to http://localhost:8080
2. Login with Supabase credentials
3. Enter test case data
4. Click "Start Analysis"
5. Wait for completion
6. Download PDF report
7. Check stats increment

---

## Expected System Behavior

### Success Indicators:
✅ All 5 agents complete successfully  
✅ Diagnosis matches expected condition  
✅ Recommended tests are relevant  
✅ Treatments are evidence-based  
✅ PDF generates and downloads  
✅ Stats increment after each case  
✅ Progress shows 0% → 100%  

### Failure Indicators:
❌ Timeout errors (> 3 minutes)  
❌ 500 Internal Server Error  
❌ No diagnosis generated  
❌ Empty treatment recommendations  
❌ PDF generation fails  
❌ Stats don't update  

---

## API Key Verification

Before testing, verify:
- [ ] `OPENROUTER_API_KEY` is set and valid
- [ ] `BIOPORTAL_API_KEY` is set and valid
- [ ] Supabase URL and anon key are configured
- [ ] Backend server is running on port 8000
- [ ] Frontend server is running on port 8080

---

## Regression Testing

After any code changes, run:
1. ✅ Test Case 1 (Diabetes) - baseline test
2. ✅ Test Case 2 (Heart Attack) - critical urgency test
3. ✅ Test Case 11 (Gastroparesis) - complex case test
4. ✅ PDF generation test
5. ✅ Stats persistence test (refresh page)

---

## Bug Reporting Template

```
**Test Case:** [Number and Name]
**Expected:** [What should happen]
**Actual:** [What actually happened]
**Error Message:** [Any error messages]
**Browser Console:** [Console errors if frontend issue]
**Backend Logs:** [Server logs if backend issue]
**Screenshots:** [Attach if relevant]
```

---

**Happy Testing! 🧪🏥**
