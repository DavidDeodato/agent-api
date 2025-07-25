-- Create doc_templates table
CREATE TABLE IF NOT EXISTS doc_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create clauses table
CREATE TABLE IF NOT EXISTS clauses (
    id SERIAL PRIMARY KEY,
    doc_template_id INTEGER NOT NULL REFERENCES doc_templates(id) ON DELETE CASCADE,
    order_num INTEGER NOT NULL,
    section_name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('mandatory', 'optional')),
    type_alternatives JSONB DEFAULT '{}',
    alert_conditions JSONB DEFAULT '{}',
    suggestions JSONB DEFAULT '{}',
    system_prompt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_template_id, order_num)
);

-- Create documents_agents table
CREATE TABLE IF NOT EXISTS documents_agents (
    id SERIAL PRIMARY KEY,
    doc_template_id INTEGER NOT NULL REFERENCES doc_templates(id) ON DELETE CASCADE,
    content JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'in_progress',
    current_clause_order INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_clauses_template_order ON clauses(doc_template_id, order_num);
CREATE INDEX IF NOT EXISTS idx_documents_agents_template ON documents_agents(doc_template_id);
CREATE INDEX IF NOT EXISTS idx_documents_agents_status ON documents_agents(status);