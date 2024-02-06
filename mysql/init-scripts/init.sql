-- init.sql
USE spotiplot;

-- Create the table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL
);

-- Create the table
CREATE TABLE tracks (
    track_id INT AUTO_INCREMENT PRIMARY KEY,
    track_title VARCHAR(100) NOT NULL,
    artists VARCHAR(100) NOT NULL,
    album VARCHAR(100) NOT NULL,
    duration_ms INT DEFAULT 0,
    acousticness FLOAT DEFAULT 0,
    danceability FLOAT DEFAULT 0,
    energy FLOAT DEFAULT 0,
    instrumentalness FLOAT DEFAULT 0,
    musical_key INT DEFAULT 0,
    liveness FLOAT DEFAULT 0,
    loudness FLOAT DEFAULT 0,
    speechiness FLOAT DEFAULT 0,
    tempo FLOAT DEFAULT 0,
    time_signature INT DEFAULT 0,
    valence FLOAT DEFAULT 0,
    uri VARCHAR(100) NOT NULL
);

-- Create the table
CREATE TABLE listening_activity (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    track_id INT,
    shuffle_state ENUM('normal', 'queue', 'shuffle', 'smart') NOT NULL,
    playback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    playback_duration_ms INT NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);
