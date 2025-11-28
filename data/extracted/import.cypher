// Neo4j Import Script - Generated from Tax Document Extraction
// This script creates nodes and relationships for the tax knowledge graph

// ============================================================================
// CREATE CONSTRAINTS
// ============================================================================

CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tax) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (tp:Taxpayer) REQUIRE tp.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agency) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Process) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (pen:Penalty) REQUIRE pen.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Deadline) REQUIRE d.id IS UNIQUE;

// ============================================================================
// CREATE INDICES
// ============================================================================

CREATE INDEX IF NOT EXISTS FOR (t:Tax) ON (t.name);
CREATE INDEX IF NOT EXISTS FOR (tp:Taxpayer) ON (tp.name);
CREATE INDEX IF NOT EXISTS FOR (a:Agency) ON (a.name);

// ============================================================================
// CREATE NODES
// ============================================================================

// Create Taxpayer nodes
MERGE (n:Taxpayer {id: 'taxpayer_1654', name: "Individual", page: 207, description: "Taxpayer type: Individual"})
MERGE (n:Taxpayer {id: 'taxpayer_1656', name: "Corporation", page: 209, description: "Taxpayer type: Corporation"})
MERGE (n:Taxpayer {id: 'taxpayer_1651', name: "Partnership", page: 207, description: "Taxpayer type: Partnership"})
MERGE (n:Taxpayer {id: 'taxpayer_1645', name: "SME", page: 207, description: "Taxpayer type: SME"})
MERGE (n:Taxpayer {id: 'taxpayer_1213', name: "Non-profit", page: 120, description: "Taxpayer type: Non-profit"})

// Create Penalty nodes
MERGE (n:Penalty {id: 'penalty_1643', name: "Late Payment Charge", page: 206, description: "Penalty: Late Payment Charge"})
MERGE (n:Penalty {id: 'penalty_1606', name: "Interest", page: 203, description: "Penalty: Interest"})
MERGE (n:Penalty {id: 'penalty_1285', name: "Non-compliance Fine", page: 127, description: "Penalty: Non-compliance Fine"})
MERGE (n:Penalty {id: 'penalty_1079', name: "Fraud Penalty", page: 103, description: "Penalty: Fraud Penalty"})

// Create Tax nodes
MERGE (n:Tax {id: 'tax_1604', name: "VAT", page: 203, description: "Tax type mentioned on page 203"})
MERGE (n:Tax {id: 'tax_1549', name: "PIT", page: 159, description: "Tax type mentioned on page 159"})
MERGE (n:Tax {id: 'tax_1658', name: "CIT", page: 215, description: "Tax type mentioned on page 215"})
MERGE (n:Tax {id: 'tax_1155', name: "CGT", page: 114, description: "Tax type mentioned on page 114"})
MERGE (n:Tax {id: 'tax_1227', name: "DST", page: 121, description: "Tax type mentioned on page 121"})
MERGE (n:Tax {id: 'tax_1376', name: "PAYE", page: 136, description: "Tax type mentioned on page 136"})

// Create Process nodes
MERGE (n:Process {id: 'process_1491', name: "Registration", page: 151, description: "Tax process: Registration"})
MERGE (n:Process {id: 'process_1653', name: "Payment", page: 207, description: "Tax process: Payment"})
MERGE (n:Process {id: 'process_1492', name: "Filing", page: 151, description: "Tax process: Filing"})
MERGE (n:Process {id: 'process_1657', name: "Audit", page: 211, description: "Tax process: Audit"})
MERGE (n:Process {id: 'process_1493', name: "Compliance", page: 151, description: "Tax process: Compliance"})
MERGE (n:Process {id: 'process_1560', name: "Appeal", page: 160, description: "Tax process: Appeal"})

// Create Deadline nodes
MERGE (n:Deadline {id: 'deadline_157', name: "within 30 days", page: 18, description: "Deadline: within 30 days"})
MERGE (n:Deadline {id: 'deadline_1034', name: "30 days", page: 99, description: "Deadline: 30 days"})
MERGE (n:Deadline {id: 'deadline_973', name: "within 12 months", page: 93, description: "Deadline: within 12 months"})

// Create Agency nodes
MERGE (n:Agency {id: 'agency_1648', name: "FIRS", page: 207, description: "Tax agency: FIRS"})

// ============================================================================
// CREATE RELATIONSHIPS
// ============================================================================

// Create applies_to relationships
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_0'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_1'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_3'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_4'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_5'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_6'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_10'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_11'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_13'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_14'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_21'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_35'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_36'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_42'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_43'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_49'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_51'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_53'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_54'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_55'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_56'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_60'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_62'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_65'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_74'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_79'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_81'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_82'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_84'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_85'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_87'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_88'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_89'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_90'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_92'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_94'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_97'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_98'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_101'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_102'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_103'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_105'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_106'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_107'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_108'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_109'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_110'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_111'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_112'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_115'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_116'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_117'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_119'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_120'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_121'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_123'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_124'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_125'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_127'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_128'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_132'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_134'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_137'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_140'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_141'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_142'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_143'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_144'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_145'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_146'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_149'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_150'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_151'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_152'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_155'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_159'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_160'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_164'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_166'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_167'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_169'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_171'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_173'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_176'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_177'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_178'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_179'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_180'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_182'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_183'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_184'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_186'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_187'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_190'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_191'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_192'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_194'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_195'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_196'}) MERGE (s)-[:applies_to]->(t)
MATCH (s:Tax {id: 'tax_9'}), (t:Taxpayer {id: 'taxpayer_199'}) MERGE (s)-[:applies_to]->(t)

// ============================================================================
// VERIFICATION QUERIES
// ============================================================================

// Count total nodes
MATCH (n) RETURN COUNT(n) as total_nodes;

// Count nodes by type
MATCH (n) RETURN labels(n)[0] as type, COUNT(n) as count ORDER BY count DESC;

// Count relationships by type
MATCH ()-[r]-() RETURN TYPE(r) as relationship, COUNT(r) as count ORDER BY count DESC;