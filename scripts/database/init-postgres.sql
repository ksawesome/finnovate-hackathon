-- @mssql: disable
-- Initialize PostgreSQL schema for finnovate-hackathon
-- Run automatically by Docker entrypoint on first start
-- Note: This is PostgreSQL syntax. T-SQL linter errors can be ignored.

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GL Accounts table
CREATE TABLE IF NOT EXISTS gl_accounts (
    id SERIAL PRIMARY KEY,
    account_code VARCHAR(50) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    entity VARCHAR(255) NOT NULL,
    balance DECIMAL(18, 2) NOT NULL,
    period VARCHAR(20) NOT NULL,
    assigned_user_id INTEGER REFERENCES users(id),
    review_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_code, entity, period)
);

-- Responsibility Matrix table
CREATE TABLE IF NOT EXISTS responsibility_matrix (
    id SERIAL PRIMARY KEY,
    gl_code VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gl_code, user_id, role)
);

-- Review Log table
CREATE TABLE IF NOT EXISTS review_log (
    id SERIAL PRIMARY KEY,
    gl_account_id INTEGER REFERENCES gl_accounts(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id),
    status VARCHAR(50) NOT NULL,
    comments TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_gl_accounts_period ON gl_accounts(period);
CREATE INDEX IF NOT EXISTS idx_gl_accounts_entity ON gl_accounts(entity);
CREATE INDEX IF NOT EXISTS idx_gl_accounts_status ON gl_accounts(review_status);
CREATE INDEX IF NOT EXISTS idx_gl_accounts_assigned ON gl_accounts(assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_review_log_gl ON review_log(gl_account_id);
CREATE INDEX IF NOT EXISTS idx_review_log_reviewer ON review_log(reviewer_id);

-- Insert sample data for testing
INSERT INTO users (name, email, department, role) VALUES
    ('John Doe', 'john.doe@adani.com', 'Finance', 'Accountant'),
    ('Jane Smith', 'jane.smith@adani.com', 'Finance', 'Manager'),
    ('Bob Johnson', 'bob.johnson@adani.com', 'Audit', 'Auditor')
ON CONFLICT (email) DO NOTHING;
