-- iajob_matcher
CREATE DATABASE iajob_matcher;

USE iajob_matcher;

-- Tabla users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    preferred_start_date DATE,
    expected_ctc VARCHAR(50),
    experience VARCHAR(50),
    skills TEXT
);

-- Tabla jobs
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    ctc_min INT,
    ctc_max INT,
    required_experience VARCHAR(50),
    skills TEXT
);

-- Tabla recommendations
CREATE TABLE recommendations (
    rec_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    job_id INT,
    relevance_score FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);


SELECT * FROM jobs
PRIMARYPRIMARYPRIMARY