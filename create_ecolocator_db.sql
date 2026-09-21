-- ============================================================
-- ECOLOCATOR DATABASE SETUP SCRIPT
-- Run this manually in MySQL Workbench or the mysql command line
-- ============================================================

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS ecolocator;
USE ecolocator;

-- 2. Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    city VARCHAR(50)
);

-- 3. Emission factors reference table
CREATE TABLE emission_factors (
    category VARCHAR(20) PRIMARY KEY,
    factor_per_unit FLOAT NOT NULL
);

-- 4. Daily log table (main data table, linked to users)
CREATE TABLE daily_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    log_date DATE,
    transport_mode VARCHAR(20),
    distance_km FLOAT DEFAULT 0,
    electricity_units FLOAT DEFAULT 0,
    meal_type VARCHAR(20),
    waste_kg FLOAT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 5. Insert default emission factors (kg CO2 per unit)
INSERT INTO emission_factors (category, factor_per_unit) VALUES
    ('car', 0.21),
    ('bike', 0.10),
    ('bus', 0.05),
    ('cycle', 0.0),
    ('walk', 0.0),
    ('electricity', 0.82),
    ('non-veg', 3.30),
    ('veg', 1.10),
    ('vegan', 0.90),
    ('waste', 0.50);

-- 6. Quick check: view all tables and confirm data
SHOW TABLES;
SELECT * FROM emission_factors;
