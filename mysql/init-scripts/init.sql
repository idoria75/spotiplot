-- init.sql

USE spotiplot;

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100),
    event_details VARCHAR(255),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO events (event_name, event_details) VALUES ('Event 1', 'Details for Event 1');
INSERT INTO events (event_name, event_details) VALUES ('Event 2', 'Details for Event 2');
-- Add more initialization data or schema changes as needed
