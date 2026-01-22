"""
Nigerian Tax Calculator - Based on Nigeria Tax Act 2025

This module provides comprehensive tax calculation functionality for Nigerian
personal income tax, including progressive tax brackets, reliefs, and deductions.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)

# Tax brackets as per Nigeria Tax Act 2025
# (upper_limit, rate) - amounts in NGN
NIGERIA_TAX_BRACKETS: List[Tuple[Decimal, Decimal]] = [
    (Decimal('300000'), Decimal('0.07')),    # First ₦300,000 at 7%
    (Decimal('300000'), Decimal('0.11')),    # Next ₦300,000 at 11%
    (Decimal('500000'), Decimal('0.15')),    # Next ₦500,000 at 15%
    (Decimal('500000'), Decimal('0.19')),    # Next ₦500,000 at 19%
    (Decimal('1600000'), Decimal('0.21')),   # Next ₦1,600,000 at 21%
    (Decimal('Infinity'), Decimal('0.24')),  # Above ₦3,200,000 at 24%
]

# Minimum tax threshold
MINIMUM_TAX_THRESHOLD = Decimal('30000000')  # ₦30 million
MINIMUM_TAX_RATE = Decimal('0.01')  # 1% minimum tax

# Consolidated Relief Allowance (CRA)
CRA_FIXED_AMOUNT = Decimal('200000')  # ₦200,000 fixed
CRA_PERCENTAGE = Decimal('0.20')  # 20% of gross income

# Pension contribution limits
PENSION_MAX_PERCENTAGE = Decimal('0.20')  # 20% max pension contribution
PENSION_EMPLOYER_RATE = Decimal('0.10')  # 10% employer contribution
PENSION_EMPLOYEE_RATE = Decimal('0.08')  # 8% employee contribution


@dataclass
class TaxBracketResult:
    """Result for a single tax bracket calculation."""
    bracket_range: str
    rate_percentage: float
    taxable_amount: Decimal
    tax_amount: Decimal


@dataclass
class TaxCalculationResult:
    """Complete tax calculation result."""
    gross_income: Decimal
    total_allowances: Decimal
    total_reliefs: Decimal
    consolidated_relief: Decimal
    taxable_income: Decimal
    tax_due: Decimal
    effective_rate: Decimal
    breakdown: List[TaxBracketResult]
    minimum_tax_applies: bool
    minimum_tax_amount: Decimal
    net_income: Decimal
    monthly_tax: Decimal


class TaxCalculationError(Exception):
    """Custom exception for tax calculation errors."""
    pass


def calculate_consolidated_relief(gross_income: Decimal) -> Decimal:
    """
    Calculate Consolidated Relief Allowance (CRA).
    CRA = ₦200,000 OR 1% of gross income, whichever is higher
    PLUS 20% of gross income
    """
    fixed_or_percentage = max(CRA_FIXED_AMOUNT, gross_income * Decimal('0.01'))
    variable_relief = gross_income * CRA_PERCENTAGE
    return fixed_or_percentage + variable_relief


def calculate_pension_relief(gross_income: Decimal, pension_contribution: Decimal = Decimal('0')) -> Decimal:
    """
    Calculate pension contribution relief.
    Employee pension contributions are tax-exempt up to 8% of basic salary.
    """
    max_exempt = gross_income * PENSION_EMPLOYEE_RATE
    return min(pension_contribution, max_exempt)


def is_taxable(annual_income: float, threshold: float = 0) -> bool:
    """
    Check if income is taxable.
    In Nigeria, there's no specific threshold - all income above reliefs is taxable.
    """
    return Decimal(str(annual_income)) > Decimal(str(threshold))


def calculate_tax_breakdown(taxable_income: Decimal) -> Tuple[Decimal, List[TaxBracketResult]]:
    """
    Calculate tax using progressive brackets.
    Returns (total_tax, breakdown_list).
    """
    total_tax = Decimal('0')
    remaining = taxable_income
    breakdown: List[TaxBracketResult] = []
    cumulative_lower = Decimal('0')
    
    for bracket_limit, rate in NIGERIA_TAX_BRACKETS:
        if remaining <= 0:
            break
            
        taxable_in_bracket = min(remaining, bracket_limit) if bracket_limit != Decimal('Infinity') else remaining
        tax_in_bracket = (taxable_in_bracket * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if taxable_in_bracket > 0:
            if bracket_limit == Decimal('Infinity'):
                bracket_range = f"Above ₦{int(cumulative_lower):,}"
            else:
                bracket_range = f"₦{int(cumulative_lower):,} - ₦{int(cumulative_lower + bracket_limit):,}"
            
            breakdown.append(TaxBracketResult(
                bracket_range=bracket_range,
                rate_percentage=float(rate * 100),
                taxable_amount=taxable_in_bracket,
                tax_amount=tax_in_bracket
            ))
            
            total_tax += tax_in_bracket
            cumulative_lower += bracket_limit if bracket_limit != Decimal('Infinity') else Decimal('0')
        
        remaining -= taxable_in_bracket
    
    return total_tax, breakdown


def calculate_minimum_tax(gross_income: Decimal) -> Decimal:
    """
    Calculate minimum tax if applicable.
    Minimum tax is 1% of gross income if gross income > ₦30 million.
    """
    if gross_income > MINIMUM_TAX_THRESHOLD:
        return (gross_income * MINIMUM_TAX_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal('0')


def calculate_tax(
    annual_income: float,
    allowances: float = 0,
    reliefs: float = 0,
    pension_contribution: float = 0,
    include_cra: bool = True
) -> TaxCalculationResult:
    """
    Calculate comprehensive tax liability for Nigerian personal income tax.
    
    Args:
        annual_income: Gross annual income in NGN
        allowances: Non-taxable allowances (housing, transport, etc.)
        reliefs: Additional tax reliefs (life insurance, etc.)
        pension_contribution: Employee pension contribution
        include_cra: Whether to automatically apply Consolidated Relief Allowance
    
    Returns:
        TaxCalculationResult with complete breakdown
    
    Raises:
        TaxCalculationError: If inputs are invalid
    """
    try:
        # Convert to Decimal for precision
        gross_income = Decimal(str(annual_income))
        total_allowances = Decimal(str(allowances))
        total_reliefs = Decimal(str(reliefs))
        pension = Decimal(str(pension_contribution))
        
        # Validate inputs
        if gross_income < 0:
            raise TaxCalculationError("Annual income cannot be negative")
        if total_allowances < 0:
            raise TaxCalculationError("Allowances cannot be negative")
        if total_reliefs < 0:
            raise TaxCalculationError("Reliefs cannot be negative")
        
        # Calculate Consolidated Relief Allowance
        cra = calculate_consolidated_relief(gross_income) if include_cra else Decimal('0')
        
        # Calculate pension relief
        pension_relief = calculate_pension_relief(gross_income, pension)
        total_reliefs += pension_relief
        
        # Calculate taxable income
        taxable_income = max(Decimal('0'), gross_income - total_allowances - total_reliefs - cra)
        
        # Calculate tax using progressive brackets
        tax_due, breakdown = calculate_tax_breakdown(taxable_income)
        
        # Check for minimum tax
        minimum_tax = calculate_minimum_tax(gross_income)
        minimum_tax_applies = minimum_tax > tax_due
        
        # Apply minimum tax if higher
        final_tax = max(tax_due, minimum_tax) if gross_income > MINIMUM_TAX_THRESHOLD else tax_due
        
        # Calculate effective rate
        effective_rate = (final_tax / gross_income * 100) if gross_income > 0 else Decimal('0')
        effective_rate = effective_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate net income
        net_income = gross_income - final_tax
        
        # Monthly tax
        monthly_tax = (final_tax / 12).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return TaxCalculationResult(
            gross_income=gross_income,
            total_allowances=total_allowances,
            total_reliefs=total_reliefs,
            consolidated_relief=cra,
            taxable_income=taxable_income,
            tax_due=final_tax,
            effective_rate=effective_rate,
            breakdown=breakdown,
            minimum_tax_applies=minimum_tax_applies,
            minimum_tax_amount=minimum_tax,
            net_income=net_income,
            monthly_tax=monthly_tax
        )
        
    except (ValueError, TypeError) as e:
        logger.error(f"Tax calculation error: {e}")
        raise TaxCalculationError(f"Invalid input values: {e}")


def format_currency(amount: Decimal) -> str:
    """Format amount as Nigerian Naira."""
    return f"₦{int(amount):,}"


def get_tax_summary(result: TaxCalculationResult) -> dict:
    """Convert TaxCalculationResult to API-friendly dictionary."""
    return {
        "gross_income": float(result.gross_income),
        "total_allowances": float(result.total_allowances),
        "total_reliefs": float(result.total_reliefs),
        "consolidated_relief": float(result.consolidated_relief),
        "taxable_income": float(result.taxable_income),
        "tax_due": float(result.tax_due),
        "effective_rate": float(result.effective_rate),
        "breakdown": [
            {
                "bracket": br.bracket_range,
                "rate": f"{br.rate_percentage}%",
                "taxable_amount": float(br.taxable_amount),
                "tax": float(br.tax_amount)
            }
            for br in result.breakdown
        ],
        "minimum_tax_applies": result.minimum_tax_applies,
        "minimum_tax_amount": float(result.minimum_tax_amount),
        "net_income": float(result.net_income),
        "monthly_tax": float(result.monthly_tax)
    }
