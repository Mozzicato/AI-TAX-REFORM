"""
Initialize NTRIA Brain with Baseline 2025 Nigerian Tax Reform Data
This ensures the RAG has answers even before any PDFs are uploaded.
"""

import os
import sys
import json
from pathlib import Path

def populate_baseline():
    print("🧠 Initializing NTRIA Knowledge Base...")
    
    # Use relative path
    base_dir = Path(__file__).parent.parent
    graph_path = base_dir / "data" / "knowledge_graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Baseline 2025 Data
    baseline_graph = {
        "nodes": {
            "VAT": {
                "name": "Value Added Tax",
                "type": "Tax",
                "description": "A consumption tax on goods and services.",
                "rate": "7.5%",
                "threshold": "₦25 million annual turnover for mandatory registration",
                "rules": "Companies with turnover below ₦25M are exempt from VAT registration."
            },
            "PIT": {
                "name": "Personal Income Tax",
                "type": "Tax",
                "description": "Tax on income of individuals, trustees, and executors.",
                "rates": [
                    {"band": "First ₦300,000", "rate": "7%"},
                    {"band": "Next ₦300,000", "rate": "11%"},
                    {"band": "Next ₦500,000", "rate": "15%"},
                    {"band": "Next ₦500,000", "rate": "19%"},
                    {"band": "Next ₦1,400,000", "rate": "21%"},
                    {"band": "Above ₦3,000,000", "rate": "24%"}
                ]
            },
            "CIT": {
                "name": "Companies Income Tax",
                "type": "Tax",
                "large_company_rate": "30%",
                "medium_company_rate": "20%",
                "small_company_rate": "0% (Turnover < ₦25M)"
            },
            "NTRIA": {
                "name": "NTRIA",
                "type": "AI Assistant",
                "purpose": "Helping Nigerians navigate the 2025 Tax Reform Act."
            }
        },
        "relationships": [
            {"source": "VAT", "type": "administered_by", "target": "FIRS"},
            {"source": "CIT", "type": "administered_by", "target": "FIRS"}
        ],
        "chunks": [
            {
                "chunk_id": "base_vat",
                "text": "The standard Value Added Tax (VAT) rate in Nigeria remains 7.5% under the 2025 reforms for most goods and services. Businesses with an annual turnover of less than ₦25 million are exempt from VAT registration and collection requirements.",
                "metadata": {"source": "Baseline Data", "page": 1}
            },
            {
                "chunk_id": "base_pit",
                "text": "Personal Income Tax (PIT) rates for 2025 follow a progressive scale: 7% for the first ₦300k, 11% for the next ₦300k, 15% for the next ₦500k, 19% for the next ₦500k, 21% for the next ₦1.4m, and 24% for anything above ₦3m.",
                "metadata": {"source": "Baseline Data", "page": 1}
            }
        ],
        "metadata": {
            "created": "2026-01-20",
            "version": "1.0",
            "description": "Baseline tax data for cold-start"
        }
    }
    
    with open(graph_path, 'w') as f:
        json.dump(baseline_graph, f, indent=2)
    
    print(f"✅ Baseline data saved to {graph_path}")
    print("🚀 RAG is now ready to answer basic questions without PDF ingestion!")

if __name__ == "__main__":
    populate_baseline()
