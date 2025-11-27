// ============================================================================
// NTRIA - Neo4j Knowledge Graph Schema
// Nigeria Tax Reform Act 2025 - Entity & Relationship Definitions
// ============================================================================

// ============================================================================
// NODE TYPES
// ============================================================================

// Tax - Represents different tax types
CREATE CONSTRAINT tax_type_unique IF NOT EXISTS 
  FOR (t:Tax) REQUIRE t.type IS UNIQUE;

// Taxpayer - Different taxpayer categories
CREATE CONSTRAINT taxpayer_category_unique IF NOT EXISTS 
  FOR (tp:Taxpayer) REQUIRE tp.category IS UNIQUE;

// Agency - Government tax agencies
CREATE CONSTRAINT agency_name_unique IF NOT EXISTS 
  FOR (a:Agency) REQUIRE a.name IS UNIQUE;

// Process - Tax processes and procedures
CREATE CONSTRAINT process_name_unique IF NOT EXISTS 
  FOR (p:Process) REQUIRE p.name IS UNIQUE;

// Deadline - Important tax deadlines
CREATE INDEX deadline_date IF NOT EXISTS 
  FOR (d:Deadline) ON (d.date);

// ============================================================================
// CREATE SAMPLE NODES
// ============================================================================

// --- TAX NODES ---
CREATE (vat:Tax {
  type: "VAT",
  rate: "7.5%",
  fullName: "Value Added Tax",
  effectiveDate: "2025-01-01",
  description: "Tax on goods and services at each stage of production",
  applicabilityThreshold: 25000000,
  thresholdType: "annual_turnover"
})
RETURN vat;

CREATE (paye:Tax {
  type: "PAYE",
  rate: "21%",
  fullName: "Pay-As-You-Earn",
  effectiveDate: "2025-01-01",
  description: "Tax on employment income",
  applicabilityThreshold: 8000000,
  thresholdType: "annual_income"
})
RETURN paye;

CREATE (dst:Tax {
  type: "DST",
  rate: "5%",
  fullName: "Digital Service Tax",
  effectiveDate: "2025-01-01",
  description: "Tax on digital services provided by non-residents",
  applicableActivities: ["streaming", "software", "digital marketing"]
})
RETURN dst;

CREATE (educationTax:Tax {
  type: "Education Tax",
  rate: "1%",
  fullName: "Education Tax",
  effectiveDate: "2025-01-01",
  description: "Tax to support education development",
  applicableTo: "all_earners"
})
RETURN educationTax;

// --- TAXPAYER NODES ---
CREATE (individual:Taxpayer {
  category: "Individual",
  description: "Natural persons earning income",
  resident: true,
  incomeThreshold: 8000000,
  complianceLevel: "Basic"
})
RETURN individual;

CREATE (freelancer:Taxpayer {
  category: "Freelancer",
  description: "Self-employed professionals",
  resident: true,
  incomeThreshold: 8000000,
  complianceLevel: "Intermediate",
  taxableActivities: ["consulting", "design", "writing"]
})
RETURN freelancer;

CREATE (sme:Taxpayer {
  category: "SME",
  description: "Small and Medium Enterprises",
  resident: true,
  annualTurnoverThreshold: 25000000,
  complianceLevel: "Intermediate"
})
RETURN sme;

CREATE (dsp:Taxpayer {
  category: "Digital Service Provider",
  description: "Providers of digital services",
  resident: false,
  applicableTaxes: ["DST"],
  complianceLevel: "Advanced"
})
RETURN dsp;

// --- AGENCY NODES ---
CREATE (firs:Agency {
  name: "FIRS",
  fullName: "Federal Inland Revenue Service",
  jurisdiction: "Federal",
  email: "info@firs.gov.ng",
  description: "Primary federal tax authority"
})
RETURN firs;

CREATE (jtb:Agency {
  name: "JTB",
  fullName: "Joint Tax Board",
  jurisdiction: "Federal",
  description: "Coordinates federal and state tax matters"
})
RETURN jtb;

// --- PROCESS NODES ---
CREATE (vatReg:Process {
  name: "VAT Registration",
  tax: "VAT",
  duration: "5-7 days",
  frequency: "Once",
  mandatory: true,
  requirements: ["Business Identification Number", "Tax Identification Number"]
})
RETURN vatReg;

CREATE (payeReg:Process {
  name: "PAYE Registration",
  tax: "PAYE",
  duration: "3-5 days",
  frequency: "Once",
  mandatory: true,
  requirements: ["Employment letter", "Tax Identification Number"]
})
RETURN payeReg;

CREATE (annualReturn:Process {
  name: "Annual Tax Return Filing",
  tax: "PAYE",
  frequency: "Annual",
  deadline: "March 31",
  mandatory: true,
  description: "File annual income tax return with FIRS"
})
RETURN annualReturn;

// --- DEADLINE NODES ---
CREATE (payeDeadline:Deadline {
  event: "Monthly PAYE Submission",
  taxType: "PAYE",
  date: "10th of each month",
  frequency: "Monthly",
  reminderDaysBefore: 3,
  penalty: "5% of tax + interest"
})
RETURN payeDeadline;

CREATE (vatDeadline:Deadline {
  event: "Quarterly VAT Return",
  taxType: "VAT",
  date: "Last day of following quarter",
  frequency: "Quarterly",
  reminderDaysBefore: 7,
  penalty: "5% of tax + interest"
})
RETURN vatDeadline;

CREATE (annualDeadline:Deadline {
  event: "Annual Income Tax Return",
  taxType: "All",
  date: "2025-03-31",
  frequency: "Annual",
  reminderDaysBefore: 30,
  penalty: "₦50,000 + interest"
})
RETURN annualDeadline;

// --- PENALTY NODES ---
CREATE (lateFiling:Penalty {
  type: "Late Filing",
  amount: 50000,
  percentage: "5%",
  calculationBasis: "tax_amount",
  description: "Penalty for filing tax returns after deadline"
})
RETURN lateFiling;

CREATE (nonPayment:Penalty {
  type: "Non-Payment",
  percentage: "10%",
  calculationBasis: "tax_amount",
  additionalCharge: "interest",
  interestRate: "5% per annum",
  description: "Penalty for not paying tax by deadline"
})
RETURN nonPayment;

// --- THRESHOLD NODES ---
CREATE (vatThreshold:Threshold {
  amount: 25000000,
  currency: "NGN",
  appliesTo: "Annual Turnover",
  logic: "above",
  taxType: "VAT",
  description: "Businesses with annual turnover above this must register for VAT"
})
RETURN vatThreshold;

// --- RULE NODES ---
CREATE (digitalServiceRule:Rule {
  content: "Non-resident digital service providers must register and pay 5% DST",
  policyRef: "Tax Reform Act 2025, Section 7",
  effectiveDate: "2025-01-01",
  status: "Active",
  applies: ["Digital Service Provider"]
})
RETURN digitalServiceRule;

// --- EXCEPTION NODES ---
CREATE (educationExemption:Exception {
  description: "Education sector exemption",
  appliesTo: "Education Services",
  conditions: ["Non-profit", "Government approved"],
  taxType: "VAT",
  effect: "Exempt from VAT"
})
RETURN educationExemption;

// --- DOCUMENT NODES ---
CREATE (taxReformAct:Document {
  title: "Tax Reform Act 2025",
  source: "Federal Government of Nigeria",
  pages: 145,
  uploadDate: "2025-01-01",
  version: "1.0",
  status: "Active"
})
RETURN taxReformAct;

// ============================================================================
// RELATIONSHIPS
// ============================================================================

// --- Tax applies to Taxpayer ---
MATCH (vat:Tax {type: "VAT"}), (sme:Taxpayer {category: "SME"})
CREATE (vat)-[:applies_to {condition: "annual_turnover > 25000000"}]->(sme);

MATCH (vat:Tax {type: "VAT"}), (sme:Taxpayer {category: "SME"})
CREATE (sme)-[:liable_for {status: "Active"}]->(vat);

// --- Tax enforced by Agency ---
MATCH (vat:Tax {type: "VAT"}), (firs:Agency {name: "FIRS"})
CREATE (vat)-[:enforced_by {since: "2025-01-01"}]->(firs);

MATCH (paye:Tax {type: "PAYE"}), (firs:Agency {name: "FIRS"})
CREATE (paye)-[:enforced_by {since: "2025-01-01"}]->(firs);

// --- Process requires Tax ---
MATCH (vatReg:Process {name: "VAT Registration"}), (vat:Tax {type: "VAT"})
CREATE (vat)-[:requires]->(vatReg);

// --- Process has Deadline ---
MATCH (vatDeadline:Deadline {event: "Quarterly VAT Return"}), (vat:Tax {type: "VAT"})
CREATE (vat)-[:has_deadline]->(vatDeadline);

// --- Penalty applies to Tax ---
MATCH (vat:Tax {type: "VAT"}), (lateFiling:Penalty {type: "Late Filing"})
CREATE (lateFiling)-[:applies_to]->(vat);

// --- Tax has Exception ---
MATCH (vat:Tax {type: "VAT"}), (exc:Exception {description: "Education sector exemption"})
CREATE (vat)-[:has_exception]->(exc);

// ============================================================================
// INDICES FOR PERFORMANCE
// ============================================================================

CREATE INDEX tax_type_idx IF NOT EXISTS FOR (t:Tax) ON (t.type);
CREATE INDEX taxpayer_category_idx IF NOT EXISTS FOR (tp:Taxpayer) ON (tp.category);
CREATE INDEX agency_name_idx IF NOT EXISTS FOR (a:Agency) ON (a.name);
CREATE INDEX deadline_date_idx IF NOT EXISTS FOR (d:Deadline) ON (d.date);
CREATE INDEX process_tax_idx IF NOT EXISTS FOR (p:Process) ON (p.tax);

// ============================================================================
// USEFUL QUERIES
// ============================================================================

// Get all taxes for a taxpayer type
MATCH (tp:Taxpayer {category: "Freelancer"})-[:liable_for]->(tax:Tax)
RETURN tax.type, tax.rate, tax.description;

// Get deadlines for a specific tax
MATCH (tax:Tax {type: "VAT"})-[:has_deadline]->(deadline:Deadline)
RETURN deadline.event, deadline.date, deadline.frequency;

// Get penalties for late payment
MATCH (penalty:Penalty)-[:applies_to]->(tax:Tax)
RETURN tax.type, penalty.type, penalty.percentage;

// Get all agencies enforcing taxes
MATCH (tax:Tax)-[:enforced_by]->(agency:Agency)
RETURN tax.type, agency.name, agency.email;

// Find exemptions for education sector
MATCH (tax:Tax)-[:has_exception]->(exc:Exception {appliesTo: "Education Services"})
RETURN tax.type, exc.description;
