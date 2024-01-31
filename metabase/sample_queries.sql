-- Most played artist
SELECT t.artists, COUNT(la.track_id) AS play_count
FROM listening_activity la
JOIN tracks t ON la.track_id = t.track_id
GROUP BY t.artists
ORDER BY play_count DESC
LIMIT 1;

-- Top 10 played songs (change limit to increase number of songs)
SELECT t.track_title, t.artists, COUNT(la.track_id) AS play_count
FROM listening_activity la
JOIN tracks t ON la.track_id = t.track_id
GROUP BY t.track_id, t.track_title, t.artists
ORDER BY play_count DESC
LIMIT 10;

-- Running since
SELECT MIN(playback_timestamp) AS first_timestamp
FROM listening_activity;

-- Number of different songs played
SELECT MAX(track_id) FROM tracks;

-- Number of songs played
SELECT MAX(activity_id) FROM listening_activity;

-- Approximate playing time (Warning: does not consider if user skipped tracks):
SELECT SUM(t.duration_ms) / 60000 AS total_play_time_minutes
FROM listening_activity la
JOIN tracks t ON la.track_id = t.track_id;
