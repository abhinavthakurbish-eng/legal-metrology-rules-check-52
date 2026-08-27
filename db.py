"""
database/db.py
--------------
SQLite database module for persistent storage of Legal Metrology compliance scans,
officer inspection records, and statutory audit trails.
"""

import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "compliance.db")


def get_connection():
    """Get SQLite database connection with row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables for compliance scans and officer audit logs."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_no TEXT UNIQUE,
            product_name TEXT NOT NULL,
            product_category TEXT DEFAULT 'General FMCG & Household',
            brand_name TEXT DEFAULT '',
            batch_no TEXT DEFAULT '',
            inspecting_officer TEXT DEFAULT 'Inspector of Legal Metrology',
            inspection_location TEXT DEFAULT 'Retail / Packaging Unit',
            image_filenames TEXT NOT NULL,
            full_text TEXT,
            overall_status TEXT NOT NULL,
            compliance_score REAL DEFAULT 0.0,
            compliance_json TEXT NOT NULL,
            ocr_low_confidence INTEGER DEFAULT 0,
            violations_count INTEGER DEFAULT 0,
            statutory_verdict TEXT DEFAULT 'PENDING',
            officer_notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_scan(product_name, image_filenames, full_text, compliance_result, ocr_low_confidence=False,
              product_category="General FMCG & Household", brand_name="", batch_no="", 
              inspecting_officer="Inspector of Legal Metrology", inspection_location="Retail / Packaging Unit"):
    """
    Save a new scan result to the database and return the scan_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    overall_status = compliance_result.get("overall_status", "NON_COMPLIANT")
    compliance_score = compliance_result.get("compliance_score", 0.0)
    violations_count = compliance_result.get("violations_count", 0)
    statutory_verdict = compliance_result.get("statutory_verdict", "DEFICIENT")

    images_json = json.dumps(image_filenames)
    compliance_json_str = json.dumps(compliance_result)

    cursor.execute("""
        INSERT INTO scans (
            product_name, product_category, brand_name, batch_no, inspecting_officer, inspection_location,
            image_filenames, full_text, overall_status, compliance_score,
            compliance_json, ocr_low_confidence, violations_count, statutory_verdict
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        product_category,
        brand_name,
        batch_no,
        inspecting_officer,
        inspection_location,
        images_json,
        full_text,
        overall_status,
        compliance_score,
        compliance_json_str,
        1 if ocr_low_confidence else 0,
        violations_count,
        statutory_verdict
    ))

    scan_id = cursor.lastrowid
    reference_no = f"LM-INSP-{datetime.now().year}-{scan_id:04d}"
    
    cursor.execute("UPDATE scans SET reference_no = ? WHERE id = ?", (reference_no, scan_id))
    
    conn.commit()
    conn.close()
    return scan_id


def get_scan_by_id(scan_id):
    """Retrieve a single scan record with parsed JSON."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    scan_dict = dict(row)
    scan_dict["image_filenames"] = json.loads(scan_dict["image_filenames"])
    scan_dict["compliance_json"] = json.loads(scan_dict["compliance_json"])
    return scan_dict


def update_officer_notes(scan_id, notes):
    """Update officer manual remarks/annotations for human-in-the-loop review."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE scans SET officer_notes = ? WHERE id = ?", (notes, scan_id))
    conn.commit()
    conn.close()


def get_all_scans(search_query="", status_filter="all", limit=100):
    """Retrieve all scans with optional search and status filter."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM scans WHERE 1=1"
    params = []

    if search_query:
        query += " AND (product_name LIKE ? OR reference_no LIKE ? OR product_category LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    if status_filter and status_filter != "all":
        query += " AND overall_status = ?"
        params.append(status_filter)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        item["image_filenames"] = json.loads(item["image_filenames"])
        item["compliance_json"] = json.loads(item["compliance_json"])
        results.append(item)
    return results


def get_dashboard_stats():
    """Calculate aggregate statistics for the officer inspection dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE overall_status = 'COMPLIANT'")
    compliant_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE overall_status = 'NON_COMPLIANT'")
    non_compliant_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE overall_status = 'PARTIAL_COMPLIANCE'")
    partial_scans = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(compliance_score) FROM scans")
    avg_score_row = cursor.fetchone()[0]
    avg_score = round(avg_score_row or 0.0, 1)

    cursor.execute("SELECT COUNT(*) FROM scans WHERE ocr_low_confidence = 1")
    low_confidence_scans = cursor.fetchone()[0]

    conn.close()

    compliance_rate = round((compliant_scans / total_scans * 100), 1) if total_scans > 0 else 0.0

    return {
        "total_scans": total_scans,
        "compliant_scans": compliant_scans,
        "non_compliant_scans": non_compliant_scans,
        "partial_scans": partial_scans,
        "avg_score": avg_score,
        "compliance_rate": compliance_rate,
        "low_confidence_scans": low_confidence_scans
    }


def update_scan_compliance(scan_id, full_text, compliance_result):
    """Update scan record with revised OCR text and recomputed compliance results."""
    conn = get_connection()
    cursor = conn.cursor()

    overall_status = compliance_result.get("overall_status", "NON_COMPLIANT")
    compliance_score = compliance_result.get("compliance_score", 0.0)
    violations_count = compliance_result.get("violations_count", 0)
    statutory_verdict = compliance_result.get("statutory_verdict", "DEFICIENT")
    compliance_json_str = json.dumps(compliance_result)

    cursor.execute("""
        UPDATE scans SET
            full_text = ?,
            overall_status = ?,
            compliance_score = ?,
            compliance_json = ?,
            violations_count = ?,
            statutory_verdict = ?
        WHERE id = ?
    """, (
        full_text,
        overall_status,
        compliance_score,
        compliance_json_str,
        violations_count,
        statutory_verdict,
        scan_id
    ))

    conn.commit()
    conn.close()

