"""Test RxNorm API connectivity and treatment agent"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.agents.treatment_agent import fetch_drug_treatments

print("=" * 80)
print("Testing RxNorm API Connectivity")
print("=" * 80)

# Test 1: Simple drug name
print("\n1. Testing with drug name 'aspirin':")
results = fetch_drug_treatments("aspirin", max_results=3)
if results:
    print(f"   ✅ SUCCESS: Found {len(results)} results")
    for r in results[:2]:
        print(f"      - {r['name']} (RXCUI: {r['rxcui']})")
else:
    print("   ❌ FAILED: No results returned")

# Test 2: Condition name
print("\n2. Testing with condition 'diabetes':")
results = fetch_drug_treatments("diabetes", max_results=3)
if results:
    print(f"   ✅ SUCCESS: Found {len(results)} results")
    for r in results[:2]:
        print(f"      - {r['name']}")
else:
    print("   ⚠️  No results (expected - conditions may not return drugs)")

# Test 3: Common medication
print("\n3. Testing with 'metformin':")
results = fetch_drug_treatments("metformin", max_results=3)
if results:
    print(f"   ✅ SUCCESS: Found {len(results)} results")
    for r in results[:2]:
        print(f"      - {r['name']} ({r['class']})")
else:
    print("   ❌ FAILED: No results returned")

print("\n" + "=" * 80)
print("RxNorm API Test Complete")
print("=" * 80)
