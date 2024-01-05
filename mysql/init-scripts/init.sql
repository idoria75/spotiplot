-- init.sql
USE spotiplot;

-- Create the table
CREATE TABLE listening_activity (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    song_title VARCHAR(255),
    artist VARCHAR(100),
    album VARCHAR(100),
    playback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO listening_activity (song_title, artist, album) VALUES ('Song 1', 'Artist 1', 'Album 1');
INSERT INTO listening_activity (song_title, artist, album) VALUES ('Song 3', 'Artist 2', 'Album 1');
INSERT INTO listening_activity (song_title, artist, album) VALUES ('Song 2', 'Artist 3', 'Album X');