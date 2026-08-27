"""
test_violations.py
------------------
Verify that rule engine catches real violations (missing tax phrase, missing net qty)
with accurate statutory penalties and deficiency remarks.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from rules_engine.engine import run_compliance_check

# Sample with violations: Missing tax inclusivity phrase, missing Net Qty unit
non_compliant_ocr = {
    "full_text": """
    SAMPLE UNBRANDED SNACK
    PRICE: Rs. 50
    PACKED BY: UNKNOWN STORE, MARKET ROAD
    PKD: 2024
    """,
    "all_words": [],
    "any_low_confidence": False
}

print("================================================================================")
print("TESTING DEFICIENT / NON-COMPLIANT PRODUCT (DEFICIENCY DETECTION)")
print("================================================================================")
result = run_compliance_check(non_compliant_ocr)

print(f"Overall Status   : {result['overall_status']}")
print(f"Compliance Score : {result['compliance_score']}%")
print(f"Statutory Verdict: {result['statutory_verdict']}")
print(f"Summary Counts   : Passed: {result['compliant_count']}, Partial: {result['partial_count']}, Violations: {result['violations_count']}")
print("-" * 80)
for r in result["results"]:
    val_clean = r['detected_value'].replace('₹', 'Rs.')
    print(f"[{r['status']:<18}] {r['rule_code']:<14} {r['rule_name']:<35} -> {val_clean}")
    if r['status'] != 'COMPLIANT':
        print(f"   -> DEFICIENCY: {r['deficiency_remarks']}")
print("================================================================================")
