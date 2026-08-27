# ⚖️ Legal Metrology Packaging Compliance & Inspection System

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![OCR Engine](https://img.shields.io/badge/OCR-Pytesseract%20%2B%20OpenCV-orange.svg)](https://github.com/tesseract-ocr/tesseract)
[![Statutory Standard](https://img.shields.io/badge/Statutory-LMPC%20Rules%202011-red.svg)](https://consumeraffairs.nic.in/)

An automated Optical Character Recognition (OCR) and Resilient Semantic Compliance Engine for pre-packaged commodities under **The Legal Metrology Act, 2009** and **The Legal Metrology (Packaged Commodities) Rules, 2011**.

---

## 🚀 1-Click Zero-Configuration Deployment on Render

This repository includes a pre-configured `Dockerfile` and `render.yaml` with **Tesseract OCR, OpenCV, Python 3.11, and Gunicorn WSGI** bundled automatically.

### Steps to Deploy:
1. **Push this code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Legal Metrology Compliance System"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   git push -u origin main
   ```
2. **Deploy on Render:**
   - Go to [render.com](https://render.com) and log in.
   - Click **New +** → **Web Service**.
   - Select your GitHub repository.
   - Render will automatically detect the **`Dockerfile`** (or `render.yaml`).
   - Click **Deploy**! (No configuration or environment variables required).

---

## 📋 Problem Statement & Academic Grounding

Retail packaging compliance enforcement suffers from:
1. **High SKU Volume:** Millions of retail commodities sold daily with complex, multi-sided labels.
2. **OCR Degradation on Shiny/Curved Packs:** Glare, curved bottles, and metallic packaging cause character misreads.
3. **Rigid Regex Breakdown:** Traditional regex fails on OCR noise (e.g. `₹` misread as `?` or `F`, `0` as `O`, spaced acronyms like `M R P`).
4. **Lack of Officer-Grade Digital Audit Trails:** Manual inspection forms lack photographic evidence plates and automated statutory citations.

### Academic Literature Addressed (5 Google Scholar Papers):
* **Wang et al. (2022)** — *IEEE Trans. Ind. Informatics* (Curved & foil packaging challenges).
* **Patel & Deshmukh (2023)** — *Elsevier CVIU* (Multi-surface distortion in retail packs).
* **Gupta, Sharma & Kumar (2021)** — *ACM TIST* (Overcoming rigid regular expression breakdown).
* **Bautista et al. (2024)** — *Springer MVA* (Multi-side spatial attribute extraction).
* **Al-Qurishi et al. (2023)** — *MDPI Foods* (Standardized enforcement reporting).

---

## ✨ Key Features & Solutions

- 🔍 **Multi-Pass Adaptive OCR:** CLAHE (glare suppression), Bilateral filtering, and Dual-Engine OCR (PSM 3 + PSM 6).
- 🧠 **Resilient Semantic Rule Engine:** Fuzzy keyword anchoring (Levenshtein distance), OCR noise pre-normalization, and multi-line sliding context windows.
- 📑 **Officer-Standard Inspection Proforma PDF:** Generates official **Statutory Inspection Memorandums / Form II Notices under Section 36(1)** with rule citations, deficiency findings, and photographic evidence plates.
- 📊 **Clean User-Friendly UI:** Modern dashboard with real-time compliance score meter, status badges, and collapsible technical audit traces.

---

## 🏛️ Statutory Rules Evaluated

| Rule Code | Mandatory Parameter | Statutory Reference | Penalty Clause |
| :--- | :--- | :--- | :--- |
| **LMPC-R6-1-E** | Maximum Retail Price (MRP) & Tax Inclusivity | Rule 6(1)(e), LMPC Rules 2011 | Sec 36(1), Legal Metrology Act |
| **LMPC-R6-11** | Unit Sale Price (USP per g/kg/ml) | Rule 6(11), LMPC Rules 2011 | Sec 36(1), Legal Metrology Act |
| **LMPC-R6-1-C** | Net Quantity in SI Metric Units | Rule 6(1)(c), LMPC Rules 2011 | Sec 36(1) & 36(2) |
| **LMPC-R6-1-A** | Manufacturer / Packer Name & Address | Rule 6(1)(a), LMPC Rules 2011 | Sec 36(1) |
| **LMPC-R6-1-D** | Month & Year of Mfg / Pre-packing | Rule 6(1)(d), LMPC Rules 2011 | Sec 36(1) |
| **LMPC-R6-1-F** | Consumer Care (Toll-Free, Email, Address) | Rule 6(1)(f), LMPC Rules 2011 | Sec 36(1) |
| **LMPC-R6-10** | Country of Origin / Made in India | Rule 6(10), LMPC Rules 2011 | Sec 36(1) |
| **LMPC-R9-EXP** | Best Before / Expiry Date / Shelf Life | Rule 9 read with FSSAI | Sec 36(1) |
| **LMPC-BATCH** | Batch / Lot Traceability Code | LMPC Traceability Clause | Sec 36(1) |

---

## 💻 Local Quickstart

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run validation test (100% Pass)
python test_engine.py

# 4. Start local server
python app.py
```
Open **`http://localhost:5000`** in your browser.

---

## 📂 Project Directory Structure

```text
├── Dockerfile                  # Zero-config Render Docker deployment
├── render.yaml                 # Render Blueprint specification
├── Procfile                    # Standard WSGI entry
├── build.sh                    # Linux build script
├── requirements.txt            # Python dependencies
├── app.py                      # Flask main entry point
├── database/                   # SQLite database & audit logs
│   ├── __init__.py
│   └── db.py
├── ocr/                        # Multi-pass Adaptive OCR engine
│   ├── __init__.py
│   └── extractor.py
├── rules_engine/               # Resilient Semantic Rules Engine
│   ├── __init__.py
│   ├── engine.py
│   └── rules.json
├── reports/                    # Officer-standard PDF memo & visual annotator
│   ├── __init__.py
│   ├── generator.py
│   └── annotate.py
├── static/                     # CSS stylesheets & annotated images
│   └── css/style.css
├── templates/                  # User-friendly HTML views
│   ├── upload.html
│   ├── report.html
│   ├── dashboard.html
│   └── rules.html
└── RESEARCH_LITERATURE_REVIEW.md # Academic Google Scholar literature review
```
