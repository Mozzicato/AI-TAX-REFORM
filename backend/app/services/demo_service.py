"""
Demo Chat Service for NTRIA
Provides mock responses when API keys are not available
"""

import random
from typing import List, Dict, Any

class DemoService:
    def __init__(self):
        # Sample tax-related responses
        self.sample_responses = [
            {
                "answer": "**Value Added Tax (VAT)** is a consumption tax imposed on goods and services in Nigeria at a standard rate of 7.5%. VAT is charged at each stage of the supply chain where value is added. \n\nKey points about VAT in Nigeria:\n\n• **Standard Rate**: 7.5% on most goods and services\n• **Zero-rated Items**: Basic food items, medical products, educational materials\n• **Exempt Items**: Financial services, residential rent, certain exports\n• **Registration Threshold**: ₦25 million annual turnover\n• **Filing**: Monthly returns required\n\nBusinesses exceeding the threshold must register with FIRS and charge VAT on their supplies.",
                "sources": [
                    {"title": "VAT Act 2020", "section": "Section 2"},
                    {"title": "FIRS VAT Guidelines", "section": "Chapter 1"}
                ],
                "confidence": 0.95
            },
            {
                "answer": "**Personal Income Tax (PIT)** in Nigeria is a progressive tax system with rates ranging from 7% to 24%.\n\n**2025 Tax Bands:**\n\n• First ₦300,000: **7%**\n• Next ₦300,000 (₦300,001 - ₦600,000): **11%** \n• Next ₦500,000 (₦600,001 - ₦1,100,000): **15%**\n• Next ₦500,000 (₦1,100,001 - ₦1,600,000): **19%**\n• Next ₦1,400,000 (₦1,600,001 - ₦3,000,000): **21%**\n• Above ₦3,000,000: **24%**\n\n**Key Allowances:**\n• Consolidated Relief Allowance: ₦200,000 + 20% of gross income (max ₦300,000)\n• Pension contributions: Up to 18% of annual income\n• Life insurance premiums\n• National Housing Fund contributions",
                "sources": [
                    {"title": "Personal Income Tax Act", "section": "Section 8"},
                    {"title": "2025 Tax Reform Guidelines", "section": "Schedule 1"}
                ],
                "confidence": 0.92
            },
            {
                "answer": "**Small and Medium Enterprises (SMEs)** in Nigeria enjoy several tax incentives under the 2025 Tax Reform:\n\n**SME Tax Rates:**\n• Micro enterprises (turnover ≤ ₦25M): **0% CIT**\n• Small enterprises (₦25M - ₦100M): **20% CIT** (reduced from 30%)\n• Medium enterprises (₦100M - ₦500M): **25% CIT**\n\n**Additional Benefits:**\n• **Pioneer Status**: 3-5 years tax holiday for qualifying sectors\n• **Investment Allowances**: Up to 100% capital allowance\n• **Export Incentives**: 0% CIT on export proceeds\n• **Research & Development**: 300% deduction on R&D expenses\n• **Employment Incentives**: Additional deductions for job creation\n\n**Compliance**: Simplified tax filing and quarterly payments for eligible SMEs.",
                "sources": [
                    {"title": "Companies Income Tax Act 2025", "section": "Section 19"},
                    {"title": "SME Development Guidelines", "section": "Chapter 3"}
                ],
                "confidence": 0.89
            },
            {
                "answer": "**Tax filing deadlines** in Nigeria for 2025:\n\n**Individual (Personal Income Tax):**\n• Self-employed: **March 31st** following the tax year\n• Employees (PAYE): Deducted monthly by employers\n\n**Companies (CIT):**\n• **June 30th** following the accounting year-end\n• Advance tax: End of 4th month of accounting year\n\n**VAT Returns:**\n• **Monthly**: 21st of the following month\n• **Annual reconciliation**: January 31st\n\n**Withholding Tax:**\n• **Monthly remittance**: 21st of following month\n\n**Penalties for late filing:**\n• ₦25,000 for first month\n• ₦5,000 for each subsequent month\n• Interest at Central Bank rate + 2% per annum",
                "sources": [
                    {"title": "FIRS Tax Filing Guidelines 2025", "section": "Section 1"},
                    {"title": "Tax Administration Act", "section": "Section 31"}
                ],
                "confidence": 0.94
            }
        ]
    
    def get_demo_response(self, message: str) -> Dict[str, Any]:
        """Return a demo response based on the message content"""
        
        # Simple keyword matching for better responses
        message_lower = message.lower().strip()
        
        # Check for greetings first
        if any(word in message_lower for word in ["hi", "hello", "hey", "greetings", "what's up", "how are you", "howdy"]):
            return {
                "answer": "Hello! 👋 I'm NTRIA (Nigeria Tax Reform Intelligence Assistant). I'm here to help you understand the 2025 Nigerian Tax Reform Act and answer any questions about taxes in Nigeria.\n\nI can help you with:\n• **Personal Income Tax (PIT)** - Understanding tax bands, deductions, and filing\n• **Value Added Tax (VAT)** - Tax rates, exemptions, and compliance\n• **Business Taxes** - Corporate income tax, SME incentives, and enterprise tax\n• **Tax Filing** - Deadlines, required documents, and procedures\n• **Tax Incentives** - Pioneer status, export benefits, and special programs\n\nWhat would you like to know about Nigerian taxes?",
                "sources": [],
                "confidence": 1.0,
                "retrieval_stats": {
                    "mode": "demo",
                    "query_type": "greeting",
                    "retrieved_chunks": 0
                },
                "valid": True
            }
        
        if any(word in message_lower for word in ["vat", "value added", "consumption", "goods", "services", "7.5", "charge"]):
            response = self.sample_responses[0]
        elif any(word in message_lower for word in ["personal income", "pit", "salary", "individual", "earn", "pay", "million", "income", "taxed", "taxing"]):
            response = self.sample_responses[1]
        elif any(word in message_lower for word in ["sme", "small business", "medium enterprise", "company", "startup", "incentive"]):
            response = self.sample_responses[2]
        elif any(word in message_lower for word in ["deadline", "filing", "due date", "when", "late", "penalty", "date"]):
            response = self.sample_responses[3]
        else:
            # Return a more helpful message if we're in demo mode
            response = {
                "answer": "I see you're asking about something specific! I'm currently running in **Demo Mode**, so I can only provide detailed answers for topics like **VAT, Personal Income Tax, SME incentives, and Filing Deadlines**.\n\nTo enable my full Graph RAG brain and have me answer *any* tax question using the live 2025 Tax Reform documents, please ensure the `GOOGLE_API_KEY` is correctly set in your environment configuration.\n\nIn the meantime, feel free to ask me about 'VAT rates' or 'How much income tax do I pay?'.",
                "sources": [],
                "confidence": 0.3,
                "retrieval_stats": {
                    "mode": "demo",
                    "query_type": "unknown-demo",
                    "retrieved_chunks": 0
                },
                "valid": True
            }
        
        return {
            "answer": response["answer"],
            "sources": response["sources"],
            "confidence": response["confidence"],
            "retrieval_stats": {
                "mode": "demo",
                "query_time_ms": 50,
                "total_chunks": 156,
                "retrieved_chunks": 5
            },
            "valid": True
        }