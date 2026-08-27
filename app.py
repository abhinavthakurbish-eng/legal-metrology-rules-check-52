"""
app.py
------
Automated Packaged Commodities Compliance & Statutory Inspection Studio
High-Performance LMPC 2011 & FSSAI Multi-Category Compliance Auditor.

Execution:
    python app.py
Open in Browser:
    http://localhost:5000 (or http://localhost:10000 on Render)
"""

import os
import uuid
import shutil
import threading
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify

from ocr.extractor import extract_text_and_boxes_multi
from rules_engine.engine import run_compliance_check, load_rules
from reports.generator import generate_pdf_report
from reports.annotate import create_annotated_image
from database import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("VERCEL") or not os.access(BASE_DIR, os.W_OK):
    UPLOAD_FOLDER = "/tmp/uploads"
    REPORTS_FOLDER = "/tmp/generated_reports"
    ANNOTATED_FOLDER = "/tmp/annotated"
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "generated_reports")
    ANNOTATED_FOLDER = os.path.join(BASE_DIR, "static", "annotated")

SAMPLES_FOLDER = os.path.join(BASE_DIR, "static", "samples")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(ANNOTATED_FOLDER, exist_ok=True)
os.makedirs(SAMPLES_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_SIDES = 6

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 * MAX_SIDES

# Initialize SQLite database schema safely
try:
    db.init_db()
except Exception as e:
    print(f"Warning during DB initialization: {e}")

# In-memory job tracking for async scan results {job_id: {"status": "pending"|"done", "scan_id": int}}
_scan_jobs = {}
_scan_jobs_lock = threading.Lock()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/healthz")
@app.route("/ping")
def health_check():
    """Render health-check endpoint."""
    return jsonify({"status": "healthy", "service": "legal-metrology-inspector", "code": 200})


@app.route("/")
def home():
    """Statutory scan upload studio & officer dashboard."""
    stats = db.get_dashboard_stats()
    rules_cfg = load_rules()
    categories = rules_cfg.get("categories", [
        "Food & Beverages", "Cosmetics & Personal Care", 
        "Consumer Electronics", "General FMCG & Household", "Imported Packaged Goods"
    ])
    return render_template("upload.html", stats=stats, categories=categories)


@app.route("/demo/<sample_id>")
def run_demo_sample(sample_id):
    """
    1-Click Instant Demo Pipeline (0.2s response):
    Instantly runs compliance check on pre-configured real FMCG product samples.
    """
    samples_data = {
        "britannia": {
            "name": "Britannia Good Day Butter Cookies 200g",
            "category": "Food & Beverages",
            "img_src": os.path.join(SAMPLES_FOLDER, "sample_britannia.jpg"),
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
            """
        },
        "fortune": {
            "name": "Fortune Sunlite Refined Sunflower Oil 1L",
            "category": "Food & Beverages",
            "img_src": os.path.join(SAMPLES_FOLDER, "sample_fortune.jpg"),
            "full_text": """
                FORTUNE SUNLITE REFINED SUNFLOWER OIL
                NET VOLUME: 1 Litre (910 g when packed)
                BATCH NO: AW2405
                PKD: 05/2024
                BEST BEFORE 9 MONTHS FROM PACKAGING
                M.R.P. Rs. 165.00 (INCLUSIVE OF ALL TAXES)
                USP: Rs. 0.16 / ml
                PACKED BY: ADANI WILMAR LTD, FORTUNE HOUSE, NEAR NAVRANGPURA, AHMEDABAD 380009, GUJARAT, INDIA
                COUNTRY OF ORIGIN: INDIA
                CONSUMER CARE: 1800-233-9999 | CAREGROUP@ADANIWILMAR.IN
            """
        },
        "deficient": {
            "name": "Unbranded Local Namkeen Snack (Deficient)",
            "category": "Food & Beverages",
            "img_src": os.path.join(SAMPLES_FOLDER, "sample_deficient.jpg"),
            "full_text": """
                UNBRANDED TASTY NAMKEEN SNACK
                QUANTITY: 150
                PRICE: Rs. 40
                PACKED AT: LOCAL SHED, MARKET ROAD
                PKD: 2024
                NO CUSTOMER CARE CELL
            """
        }
    }

    sample = samples_data.get(sample_id, samples_data["britannia"])
    unique_filename = f"sample_{sample_id}_{uuid.uuid4().hex[:6]}.jpg"
    dest_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    if os.path.exists(sample["img_src"]):
        shutil.copy(sample["img_src"], dest_path)
    else:
        with open(dest_path, "wb") as f:
            f.write(b"")

    ocr_result = {
        "full_text": sample["full_text"],
        "normalized_text": sample["full_text"],
        "all_words": [
            {"text": "MRP", "confidence": 95, "bbox": [80, 250, 60, 25], "image_index": 0, "line_num": 1},
            {"text": "Rs.", "confidence": 95, "bbox": [150, 250, 40, 25], "image_index": 0, "line_num": 1},
            {"text": "NET", "confidence": 95, "bbox": [80, 120, 50, 25], "image_index": 0, "line_num": 2},
            {"text": "QUANTITY", "confidence": 95, "bbox": [135, 120, 90, 25], "image_index": 0, "line_num": 2},
        ],
        "side_results": [],
        "total_sides": 1,
        "any_low_confidence": False
    }

    compliance_result = run_compliance_check(ocr_result, product_category=sample["category"])

    scan_id = db.save_scan(
        product_name=sample["name"],
        product_category=sample["category"],
        image_filenames=[unique_filename],
        full_text=sample["full_text"],
        compliance_result=compliance_result,
        ocr_low_confidence=False
    )

    annotated_filename = f"annotated_{unique_filename}"
    annotated_path = os.path.join(ANNOTATED_FOLDER, annotated_filename)
    try:
        create_annotated_image(dest_path, compliance_result["results"], annotated_path, image_index=0)
    except Exception:
        pass

    return redirect(url_for("view_report", scan_id=scan_id))


@app.route("/scan", methods=["POST"])
def scan():
    """
    Sub-Second Parallel Execution Pipeline:
    1. Multi-side high-res images uploaded
    2. Concurrent multi-threaded OCR (<1.5s)
    3. Category-specific LMPC 2011 statutory rule verification
    4. Save audit trail & generate bounding box overlays
    5. Redirect to Interactive Inspection Studio
    """
    files = [f for f in request.files.getlist("label_images") if f and f.filename]
    product_name = request.form.get("product_name", "").strip() or "Standard Packaged Commodity"
    product_category = request.form.get("product_category", "").strip() or "General FMCG & Household"

    if not files:
        return "No package photograph provided. Please upload at least one image.", 400

    if len(files) > MAX_SIDES:
        return f"Maximum {MAX_SIDES} images permitted per package audit.", 400

    for f in files:
        if not allowed_file(f.filename):
            return f"Invalid file format: {f.filename}. Permitted: PNG, JPG, JPEG, WEBP.", 400

    unique_filenames = []
    image_paths = []
    for f in files:
        ext = f.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        f.save(image_path)
        unique_filenames.append(unique_filename)
        image_paths.append(image_path)




    # 1. Fast Parallel OCR Extraction
    try:
        ocr_result = extract_text_and_boxes_multi(image_paths)
    except Exception as e:
        return f"Error during Optical Character Recognition: {str(e)}", 500

    # Optional Inspector-Assisted Package Metadata Cross-Validation
    declared_net_qty = request.form.get("declared_net_qty", "").strip()
    declared_mrp = request.form.get("declared_mrp", "").strip()
    declared_mfg_date = request.form.get("declared_mfg_date", "").strip()
    declared_batch_no = request.form.get("declared_batch_no", "").strip()

    declared_lines = []
    if declared_net_qty:
        declared_lines.append(f"NET QUANTITY: {declared_net_qty}")
    if declared_mrp:
        declared_lines.append(f"MRP: {declared_mrp} (INCL. OF ALL TAXES)")
    if declared_mfg_date:
        declared_lines.append(f"MFD DATE: {declared_mfg_date}")
    if declared_batch_no:
        declared_lines.append(f"BATCH NO: {declared_batch_no}")

    if declared_lines:
        declared_block = "\n--- [INSPECTOR DECLARED SPECIFICATIONS] ---\n" + "\n".join(declared_lines)
        ocr_result["full_text"] += "\n" + declared_block
        ocr_result["normalized_text"] += "\n" + declared_block

    # 2. Statutory Compliance Check with Category Context
    compliance_result = run_compliance_check(ocr_result, product_category=product_category)


    # 3. Save Inspection Record to Database
    scan_id = db.save_scan(
        product_name=product_name,
        product_category=product_category,
        image_filenames=unique_filenames,
        full_text=ocr_result["full_text"],
        compliance_result=compliance_result,
        ocr_low_confidence=ocr_result.get("any_low_confidence", False)
    )

    # 4. Generate Visual Evidence Annotations (Asynchronous / Non-blocking)
    def _async_annotate():
        for idx, unique_filename in enumerate(unique_filenames):
            annotated_filename = f"annotated_{unique_filename}"
            annotated_path = os.path.join(ANNOTATED_FOLDER, annotated_filename)
            try:
                create_annotated_image(
                    image_paths[idx], compliance_result["results"], annotated_path, image_index=idx
                )
            except Exception:
                pass

    threading.Thread(target=_async_annotate, daemon=True).start()

    return redirect(url_for("view_report", scan_id=scan_id))



@app.route("/report/<int:scan_id>")
def view_report(scan_id):
    """View official inspection studio, interactive canvas, and statutory audit matrix."""
    scan = db.get_scan_by_id(scan_id)
    if scan is None:
        return "Inspection record not found", 404

    images = []
    for idx, filename in enumerate(scan["image_filenames"]):
        annotated_filename = f"annotated_{filename}"
        annotated_exists = os.path.exists(os.path.join(ANNOTATED_FOLDER, annotated_filename))
        images.append({
            "side_num": idx + 1,
            "filename": annotated_filename if annotated_exists else filename,
            "annotated": annotated_exists
        })

    raw_ocr_text = scan.get("full_text", "")
    ocr_low_confidence = bool(scan.get("ocr_low_confidence", 0))

    return render_template(
        "report.html",
        scan=scan,
        compliance=scan["compliance_json"],
        images=images,
        raw_ocr_text=raw_ocr_text,
        ocr_low_confidence=ocr_low_confidence
    )


@app.route("/report/<int:scan_id>/update-notes", methods=["POST"])
def update_notes(scan_id):
    """Human-in-the-loop: Save officer remarks or manual regulatory override."""
    notes = request.form.get("officer_notes", "").strip()
    db.update_officer_notes(scan_id, notes)
    return redirect(url_for("view_report", scan_id=scan_id))


@app.route("/report/<int:scan_id>/re-audit", methods=["POST"])
def re_audit(scan_id):
    """
    Human-in-the-loop / Officer Re-audit:
    Allows user/inspector to review or adjust scanned text and re-run compliance audit instantly (0.1s).
    """
    scan = db.get_scan_by_id(scan_id)
    if scan is None:
        return "Inspection record not found", 404

    edited_text = request.form.get("scanned_text", "").strip()
    if not edited_text:
        edited_text = scan.get("full_text", "")

    product_category = scan.get("product_category", "General FMCG & Household")

    ocr_result = {
        "full_text": edited_text,
        "normalized_text": edited_text,
        "all_words": [],
        "side_results": [],
        "total_sides": len(scan.get("image_filenames", [])),
        "any_low_confidence": False
    }

    compliance_result = run_compliance_check(ocr_result, product_category=product_category)
    db.update_scan_compliance(scan_id, edited_text, compliance_result)

    return redirect(url_for("view_report", scan_id=scan_id))



@app.route("/report/<int:scan_id>/pdf")
def download_pdf(scan_id):
    """Download official Officer-Standard Legal Metrology Inspection Memorandum (PDF)."""
    scan = db.get_scan_by_id(scan_id)
    if scan is None:
        return "Inspection record not found", 404

    image_paths = [os.path.join(UPLOAD_FOLDER, fname) for fname in scan["image_filenames"]]
    pdf_filename = f"statutory_inspection_memo_{scan_id}.pdf"
    pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)

    generate_pdf_report(
        scan_id=scan_id,
        product_name=scan["product_name"],
        image_paths=image_paths,
        compliance_result=scan["compliance_json"],
        output_path=pdf_path
    )

    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)


@app.route("/dashboard")
def dashboard():
    """Case register and historical inspection audit trail."""
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")

    scans = db.get_all_scans(search_query=search_query, status_filter=status_filter)
    stats = db.get_dashboard_stats()

    return render_template(
        "dashboard.html",
        scans=scans,
        stats=stats,
        search_query=search_query,
        status_filter=status_filter
    )


@app.route("/rules")
def view_rules():
    """Statutory Legal Metrology rule book & competitive benchmark matrix."""
    rules = load_rules()
    return render_template("rules.html", rules=rules)


@app.route("/uploads/<filename>")
def serve_upload(filename):
    """Serve uploaded package images."""
    return send_file(os.path.join(UPLOAD_FOLDER, filename))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server running on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)
