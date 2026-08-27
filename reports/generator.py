"""
reports/generator.py
--------------------
Official Legal Metrology Officer-Standard Inspection Report Generator (PDF).

Generates a statutory inspection proforma adhering to the format used by
Legal Metrology Inspectors and Food Safety Officers under the
Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011.
"""

import os
from datetime import datetime

REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(scan_id, product_name, image_paths, compliance_result, output_path):
    """
    Generate an official Officer-Standard Legal Metrology Compliance Inspection Report in PDF.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not REPORTLAB_AVAILABLE:
        # Generate clean HTML/text fallback if ReportLab is not yet installed
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"DIRECTORATE OF LEGAL METROLOGY - STATUTORY INSPECTION MEMORANDUM\n")
            f.write(f"Case Ref: LM-INSP-2026-{scan_id:04d}\n")
            f.write(f"Product: {product_name}\n")
            f.write(f"Verdict: {compliance_result.get('statutory_verdict')}\n")
            f.write(f"Score: {compliance_result.get('compliance_score')}%\n")
        return output_path

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        alignment=1,
        textColor=colors.HexColor('#0f2b48')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#4a5568')
    )

    memo_style = ParagraphStyle(
        'MemoHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        alignment=1,
        textColor=colors.HexColor('#c53030')
    )

    section_heading = ParagraphStyle(
        'SectionHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f2b48'),
        spaceAfter=5
    )

    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#1a202c'))
    cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor('#2d3748'))
    cell_pass = ParagraphStyle('CellPass', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#1e7e34'))
    cell_warn = ParagraphStyle('CellWarn', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#d97706'))
    cell_fail = ParagraphStyle('CellFail', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#dc2626'))
    legal_text = ParagraphStyle('LegalText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#4a5568'))

    story = []

    # 1. Statutory Header
    story.append(Paragraph("DIRECTORATE OF LEGAL METROLOGY & CONSUMER AFFAIRS", title_style))
    story.append(Paragraph("ENFORCEMENT WING — PACKAGED COMMODITIES INSPECTION DIVISION", subtitle_style))
    story.append(Paragraph("STATUTORY INSPECTION MEMORANDUM & COMPLIANCE FINDINGS", memo_style))
    story.append(Paragraph("Under Section 15 & Section 36 of The Legal Metrology Act, 2009 read with LMPC Rules, 2011", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f2b48'), spaceAfter=6))

    # 2. Case Metadata
    ref_no = f"LM-INSP-{datetime.now().year}-{scan_id:04d}"
    insp_date = datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")

    meta_data = [
        [Paragraph("<b>Inspection Ref No:</b>", cell_normal), Paragraph(f"<b>{ref_no}</b>", cell_bold), Paragraph("<b>Date/Time:</b>", cell_normal), Paragraph(insp_date, cell_normal)],
        [Paragraph("<b>Commodity Inspected:</b>", cell_normal), Paragraph(f"<b>{product_name}</b>", cell_bold), Paragraph("<b>Inspecting Authority:</b>", cell_normal), Paragraph("Inspector of Legal Metrology", cell_normal)],
        [Paragraph("<b>Inspection Premise:</b>", cell_normal), Paragraph("Retail Packaging / Distribution Center", cell_normal), Paragraph("<b>Governing Regulation:</b>", cell_normal), Paragraph("LMPC Rules, 2011 & FSSAI", cell_normal)]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 3. Verdict Summary
    overall_status = compliance_result.get("overall_status", "NON_COMPLIANT")
    score = compliance_result.get("compliance_score", 0.0)
    verdict = compliance_result.get("statutory_verdict", "DEFICIENT")
    violations = compliance_result.get("violations_count", 0)
    compliant_count = compliance_result.get("compliant_count", 0)
    partial_count = compliance_result.get("partial_count", 0)

    verdict_style = ParagraphStyle(
        'VerdictText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13,
        textColor=colors.HexColor('#065f46') if overall_status == 'COMPLIANT' else (colors.HexColor('#92400e') if overall_status == 'PARTIAL_COMPLIANCE' else colors.HexColor('#991b1b'))
    )

    verdict_summary = [
        [Paragraph(f"<b>OFFICIAL VERDICT:</b> {verdict}", verdict_style), Paragraph(f"<b>LMPC Compliance Score:</b> {score}%", verdict_style)],
        [Paragraph(f"<b>Total Clauses:</b> {compliance_result.get('total_rules', 9)} | <b>Passed:</b> {compliant_count} | <b>Partial:</b> {partial_count} | <b>Violations:</b> {violations}", cell_normal), Paragraph(f"<b>Status:</b> <b>{overall_status}</b>", cell_bold)]
    ]

    verdict_table = Table(verdict_summary, colWidths=[340, 180])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 10))

    # 4. Audit Table
    story.append(Paragraph("CLAUSE-BY-CLAUSE STATUTORY COMPLIANCE AUDIT MATRIX", section_heading))
    table_data = [
        [Paragraph("<b>Sl.</b>", cell_bold), Paragraph("<b>Statutory Rule</b>", cell_bold), Paragraph("<b>Detected Label Declaration</b>", cell_bold), Paragraph("<b>Status</b>", cell_bold), Paragraph("<b>Deficiency Findings & Penalty</b>", cell_bold)]
    ]

    results = compliance_result.get("results", [])
    for idx, r in enumerate(results, 1):
        st = r.get("status", "NON_COMPLIANT")
        st_cell = Paragraph("PASS", cell_pass) if st == "COMPLIANT" else (Paragraph("PARTIAL", cell_warn) if st == "PARTIAL_COMPLIANCE" else Paragraph("FAIL", cell_fail))

        rule_col = f"<b>{r.get('rule_code')}</b> - {r.get('rule_name')}<br/><font color='#64748b' size='5.5'>{r.get('statutory_reference')}</font>"
        detected_col = f"<b>{r.get('detected_value', 'N/A')}</b>"
        remark_col = f"{r.get('deficiency_remarks', '')}<br/><font color='#991b1b' size='5.5'><b>Penalty:</b> {r.get('penalty_clause', '')}</font>"

        table_data.append([Paragraph(str(idx), cell_normal), Paragraph(rule_col, cell_normal), Paragraph(detected_col, cell_normal), st_cell, Paragraph(remark_col, cell_normal)])

    audit_table = Table(table_data, colWidths=[18, 132, 130, 45, 195])
    audit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2b48')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(audit_table)
    story.append(Spacer(1, 10))

    # 5. Signatory Block
    notice_text = (
        "<b>STATUTORY NOTICE:</b> This memorandum is generated under The Legal Metrology Act, 2009. "
        "Where non-compliances are recorded above, the manufacturer/packer/importer is liable for action under Section 36(1)."
    )
    story.append(Paragraph(notice_text, legal_text))
    story.append(Spacer(1, 10))

    sign_data = [
        [
            Paragraph("<b>Inspected By:</b><br/><br/><br/>_______________________________<br/><b>Inspector of Legal Metrology</b><br/>Enforcement Wing / Official Seal", cell_normal),
            Paragraph("<b>Acknowledged By (Trader / Packer):</b><br/><br/><br/>_______________________________<br/><b>Authorized Representative Signature</b><br/>Premise Stamp & Date", cell_normal)
        ]
    ]
    sign_table = Table(sign_data, colWidths=[260, 260])
    sign_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([sign_table]))

    doc.build(story)
    return output_path
