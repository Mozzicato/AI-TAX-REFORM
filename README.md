# AI-TAX-REFORM

A simple project to build a Nigerian tax-help chatbot and a basic tax calculator using the new tax laws effective from January 1.

Goals
- Provide a retrieval-augmented chatbot that answers questions about the new tax laws (ingest PDF).
- Offer a tax calculator for users falling under the taxable threshold.
- Ship a minimal web UI for interaction.

Quick start (local)
1. Place the official tax PDF inside `data/raw/` (filename: `nigeria_tax_laws.pdf`).
2. Create a Python virtual environment and install deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Run the ingest script (will parse PDF and build embeddings):

```powershell
python scripts/ingest_pdf.py --pdf data/raw/nigeria_tax_laws.pdf
```

4. Start the web UI (Flask/FastAPI):

```powershell
python app.py
```

Where to put the PDF
- Put the official PDF in `data/raw/` and name it `nigeria_tax_laws.pdf` so the ingestion script finds it.

What's included
- Basic project scaffold (to be created): ingestion, QA agent, tax calculator, minimal UI.

Next steps
- Ingest the PDF and implement the retrieval QA agent.
- Implement and verify the tax calculator logic against the law text.

License & notes
- This project is an informational tool; not legal or tax advice.

