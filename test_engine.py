"""
test_engine.py
--------------
Unit test to verify that real-world retail package texts correctly pass compliance checks
without false negative RED CROSSES on MRP, Net Qty, Dates, etc.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from rules_engine.engine import run_compliance_check

# Sample realistic noisy OCR output from Indian FMCG package (e.g. Britannia / Parle / Fortune)
sample_ocr_output = {
    "full_text": """
    BRITANNIA GOOD DAY BUTTER COOKIES
    NET QUANTITY: 200 g
    BATCH NO: B24089A
    MFD: 08/2024
    BEST BEFORE 9 MONTHS FROM PACKAGING
    M.R.P. Rs. 45.00 (INCL. OF ALL TAXES)
    USP: Rs. 0.22 / g
    MANUFACTURED BY: BRITANNIA INDUSTRIES LTD, PLOT 14, BOMMASANDRA INDUSTRIAL AREA, BANGALORE 560099, KARNATAKA, INDIA
    COUNTRY OF ORIGIN: INDIA
    CONSUMER CARE: CALL TOLL-FREE 1800-425-4449 OR EMAIL FEEDBACK@BRITANNIA.CO.IN
    """,
    "all_words": [
        {"text": "M.R.P.", "confidence": 92, "bbox": [100, 200, 80, 25], "image_index": 0, "line_num": 1},
        {"text": "Rs.", "confidence": 95, "bbox": [190, 200, 40, 25], "image_index": 0, "line_num": 1},
        {"text": "45.00", "confidence": 94, "bbox": [240, 200, 60, 25], "image_index": 0, "line_num": 1},
        {"text": "INCL.", "confidence": 88, "bbox": [310, 200, 50, 25], "image_index": 0, "line_num": 1},
        {"text": "OF", "confidence": 90, "bbox": [365, 200, 30, 25], "image_index": 0, "line_num": 1},
        {"text": "ALL", "confidence": 91, "bbox": [400, 200, 40, 25], "image_index": 0, "line_num": 1},
        {"text": "TAXES", "confidence": 93, "bbox": [445, 200, 60, 25], "image_index": 0, "line_num": 1},
        {"text": "NET", "confidence": 95, "bbox": [100, 100, 40, 25], "image_index": 0, "line_num": 2},
        {"text": "QUANTITY", "confidence": 94, "bbox": [145, 100, 90, 25], "image_index": 0, "line_num": 2},
        {"text": "200", "confidence": 96, "bbox": [240, 100, 40, 25], "image_index": 0, "line_num": 2},
        {"text": "g", "confidence": 92, "bbox": [285, 100, 20, 25], "image_index": 0, "line_num": 2},
    ],
    "any_low_confidence": False
}

print("================================================================================")
print("TESTING COMPLIANCE CHECK ON REALISTIC PACKAGED COMMODITY")
print("================================================================================")
result = run_compliance_check(sample_ocr_output)

print(f"Overall Status   : {result['overall_status']}")
print(f"Compliance Score : {result['compliance_score']}%")
print(f"Statutory Verdict: {result['statutory_verdict']}")
print(f"Summary Counts   : Passed: {result['compliant_count']}, Partial: {result['partial_count']}, Violations: {result['violations_count']}")
print("-" * 80)
for r in result["results"]:
    val_clean = r['detected_value'].replace('₹', 'Rs.')
    print(f"[{r['status']:<18}] {r['rule_code']:<14} {r['rule_name']:<35} -> {val_clean}")
print("================================================================================")
