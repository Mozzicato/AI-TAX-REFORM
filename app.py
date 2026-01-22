from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
app = Flask(__name__)

from src.tax_calculator import is_taxable, calculate_tax


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}
    income = data.get("income")
    if income is None:
        return jsonify({"error": "missing 'income' field"}), 400
    try:
        income = float(income)
    except Exception:
        return jsonify({"error": "invalid income"}), 400
    taxable, tax_amount = calculate_tax(income)
    return jsonify({"taxable": taxable, "tax_amount": tax_amount})


@app.route("/retrieve", methods=["POST"])
def retrieve():
    payload = request.get_json() or {}
    query = payload.get("query")
    top_k = int(payload.get("top_k", 5))
    if not query:
        return jsonify({"error": "missing 'query'"}), 400

    # Basic retrieval using local scripts (requires vectorstore built)
    try:
        from scripts.query_qa import load_vectorstore, query
    except Exception as e:
        return jsonify({"error": "query module not available", "detail": str(e)}), 500

    index, docs = load_vectorstore()
    results = query(index, docs, query, top_k=top_k)
    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
