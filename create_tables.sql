CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    role VARCHAR(25),
    department VARCHAR(50),
    designation VARCHAR(50),
    office_location VARCHAR(50),
    password_hash TEXT,
    is_active VARCHAR(10),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    assigned_to UUID REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    due_date TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE task_status (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    status VARCHAR(20), -- e.g., Assigned, In Progress, Submitted, Approved, Rejected
    created_at TIMESTAMP
);

CREATE TABLE gps_logs (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    latitude NUMERIC,
    longitude NUMERIC,
    timestamp TIMESTAMP
);

CREATE TABLE evidence (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    file_path TEXT,
    uploaded_at TIMESTAMP
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    manager_id UUID REFERENCES users(id),
    status VARCHAR(10), -- Approved/Rejected
    feedback TEXT,
    reviewed_at TIMESTAMP
);
