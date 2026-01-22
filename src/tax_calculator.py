"""Simple tax calculator helpers.
This module provides a minimal `is_taxable` helper and a placeholder `calculate_tax` function.
Update the thresholds and bands to match the Nigeria-Tax-Act-2025 text before using for real calculations.
"""

DEFAULT_TAX_THRESHOLD = 300000  # placeholder annual threshold; verify against law


def is_taxable(annual_income, threshold=DEFAULT_TAX_THRESHOLD):
    return annual_income > threshold


def calculate_tax(annual_income, threshold=DEFAULT_TAX_THRESHOLD):
    """Return (is_taxable, tax_amount). For now, returns 0 if below threshold, else returns a placeholder flat 7%.
    Replace with correct progressive band logic using the official law.
    """
    if not is_taxable(annual_income, threshold):
        return False, 0.0
    tax_amount = (annual_income - threshold) * 0.07
    return True, round(tax_amount, 2)
