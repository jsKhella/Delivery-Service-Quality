# Delivery: Olist delivery service quality

Made by CURIOSITY on 2026-11-20 19:28 from report **20261120T171130-3819d347a5** (job J0001-olist-delivery-service-quality).

## deliverables/
The files to share. Every one was checked against the report before it got here:
- `dashboard_v1.html`
- `dashboard_v1.pdf`
- `dashboard_v2.html`
- `dashboard_v2.pdf`
- `dashboard_v3.html`
- `dashboard_v3.pdf`
- `dashboard_v3.xlsx`
- `dashboard_v4.html`
- `dashboard_v4.pdf`
- `dashboard_v4.xlsx`
- `dashboard_v5.html`
- `dashboard_v5.pdf`
- `dashboard_v5.xlsx`
- `pdf_brief_v1.html`
- `pdf_brief_v1.pdf`
- `pdf_brief_v1.xlsx`
- `pdf_brief_v2.html`
- `pdf_brief_v2.pdf`
- `pdf_brief_v2.xlsx`
- `pdf_brief_v3.html`
- `pdf_brief_v3.pdf`
- `pdf_brief_v3.xlsx`
- `pdf_brief_v4.html`
- `pdf_brief_v4.pdf`
- `pdf_brief_v4.xlsx`
- `pdf_brief_v5.html`
- `pdf_brief_v5.pdf`
- `pdf_brief_v5.xlsx`
- `pdf_brief_v6.html`
- `pdf_brief_v6.pdf`
- `pdf_brief_v6.xlsx`
- `pdf_brief_v8.html`
- `pdf_brief_v8.pdf`
- `pdf_brief_v8.xlsx`
- `report_20261120T171130.docx`
- `report_20261120T171130.xlsx`
- `report_20261120T171130_data`
- `report_20261120T171130_figures`

## REPRODUCIBILITY/
Everything needed to compute every number again, from the original sources:

1. Install Python 3.13 and the packages in `requirements.txt` (`pip install -r requirements.txt`).
2. Get each source file listed in `SOURCES.md` and put it in `job/raw/` under the name given there
   (9 file(s); `reproduce.py` checks each one's fingerprint, so a different version is caught).
3. Run `python reproduce.py` inside the REPRODUCIBILITY folder.

It re-runs every step's code in the original order (11 steps), then compares every output file and every
number (102 results) with what the report used. It ends with REPRODUCED (all identical) or lists what differs.
`plan.yaml` and `brief.md` define every number; `job/steps/Sxx/blind_redo/` holds the independent second method
used to double-check the critical steps (for reading).
