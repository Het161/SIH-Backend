-- User table (managers, employees)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    role VARCHAR(25),
    department VARCHAR(50),
    designation VARCHAR(50),
    office_location VARCHAR(50),
    password_hash TEXT,
    is_active VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(100),
    description TEXT,
    assigned_to UUID REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task status history
CREATE TABLE IF NOT EXISTS task_status (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    status VARCHAR(20), -- Assigned, In Progress, Submitted, Approved, Rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GPS logs
CREATE TABLE IF NOT EXISTS gps_logs (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    latitude NUMERIC,
    longitude NUMERIC,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evidence uploads
CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task reviews
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    manager_id UUID REFERENCES users(id),
    status VARCHAR(10), -- Approved/Rejected
    feedback TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE task_status (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gps_logs (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    latitude NUMERIC,
    longitude NUMERIC,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    manager_id UUID REFERENCES users(id),
    status VARCHAR(10),
    feedback TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS task_status (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
