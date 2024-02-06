import os
import time
import spotipy
import mysql.connector
from spotipy.oauth2 import SpotifyOAuth
from yaml import safe_load
from mysql.connector import errorcode
from track import Track
import traceback

PATH_TO_KEYS = "/app/spotiplot.env"
DEBUG_STATE = False

db_pass = os.getenv("MYSQL_PASSWORD")

db_config = {
    "user": "spotiplot",
    "password": db_pass,
    "host": "mysql",
    "port": 3306,
    "database": "spotiplot",
}


class Monitor:
    def __init__(self):
        print("Starting spotiplot monitor")
        self.authenticate_db()
        self.authenticate_spotify()

        self.last_played = []
        self.current_track = None
        self.last_track = None

        self.user_db_id = self.get_user_db_id()
        if self.user_db_id == 0:
            print("User not in the database")
            if not self.insert_user_db():
                exit()

    def authenticate_db(self):
        connected = False
        while not (connected):
            try:
                conn = mysql.connector.connect(**db_config)
                print("Connected to MySQL database!")
                connected = True
                conn.close()

            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Failed to authenticate with database!")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)

            except BaseException as e:
                print("Exception: {}".format(e))
                traceback.print_exc()

            if not (connected):
                time.sleep(5)

    def authenticate_spotify(self):
        try:
            with open(PATH_TO_KEYS, "r") as file:
                vars = safe_load(file).get("credentials")
                id = vars.get("client_id")
                secret = vars.get("client_secret")
                uri = vars.get("redirect_uri")

            scope = "user-read-playback-state, user-read-currently-playing, user-read-recently-played"

            ch = spotipy.CacheFileHandler("cache/.cache")

            auth_manager = SpotifyOAuth(
                scope=scope,
                client_id=id,
                client_secret=secret,
                redirect_uri=uri,
                open_browser=False,
                cache_handler=ch,
            )

            # print("ID: {}\n Secret: {}\n URI: {}".format(id, secret, uri))

            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.current_user = self.sp.current_user()["display_name"]

        except BaseException as e:
            print("Failed to read user credentials. Error: {}".format(e))
            exit()

        print("Spotify authentication succeeded for user: {}".format(self.current_user))

    def get_user_db_id(self):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        user_id = 0

        for row in rows:
            row_id = row[0]
            row_user = row[1]
            if self.current_user == row_user:
                user_id = row_id
                break

        cursor.close()
        conn.close()
        return user_id

    def insert_user_db(self):
        if self.current_user is not None:
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                insert_query = "INSERT INTO users (user_name) VALUES (%s)"
                data_to_insert = [self.current_user]

                cursor.execute(insert_query, data_to_insert)
                conn.commit()

                cursor.close()
                conn.close()

                print(
                    "Saved user {} to db with id {}".format(
                        self.current_user, self.get_user_db_id()
                    )
                )
                return True

            except BaseException as e:
                print("Exception: {}".format(e))
                traceback.print_exc()
                return False

        else:
            print("Nothing to write to DB!")
            return False

    def parse_artists_list(self, a_artists=[]):
        artists = ""

        if a_artists:
            for i in range(len(a_artists) - 1):
                artists = artists + a_artists[i]["name"] + ", "

            artists = artists + a_artists[-1]["name"]

        else:
            artists = "invalid artist info"

        return artists

    def get_recently_played(self):
        res_list = self.sp.current_user_recently_played(limit=10)
        items = res_list["items"]

        tracks = []

        for i in range(len(items)):
            tracks.append(
                Track(
                    a_title=items[i]["track"]["name"],
                    a_artists=items[i]["track"]["artists"],
                )
            )

        for track in tracks:
            print(track)

    # TODO: Implement queue monitor
    def get_queue(self):
        sp_queue = self.sp.queue()["queue"]
        queue = []

        print("Number of items in queue: {}".format(len(sp_queue)))

        for item in queue:
            t = Track(
                a_title=item["name"],
                a_artists=self.parse_artists_list(item["artists"]),
                a_album=item["album"]["name"],
                a_uri=item["uri"],
                a_duration_ms=item["duration_ms"],
            )

            queue.append(t)

        for track in queue:
            print(track)

    def update_currently_playing(self):
        try:
            result = self.sp.current_playback()

            if result is not None:
                shuffle_state = "normal"

                if result["smart_shuffle"]:
                    shuffle_state = "smart"

                elif result["shuffle_state"]:
                    shuffle_state = "shuffle"

                if DEBUG_STATE:
                    print("Current playback state:")
                    print("Shuffle state: {}".format(result["shuffle_state"]))
                    print("Smart shuffle: {}".format(result["smart_shuffle"]))
                    print("Repeat state: {}".format(result["repeat_state"]))
                    print("Is playing: {}".format(result["is_playing"]))
                    print("Type: {}".format(result["context"]["type"]))
                    print("Playlist URI: {}".format(result["context"]["uri"]))

                    print("Shuffle state: {}".format(shuffle_state))

                item = result["item"]

                t = Track(
                    a_title=item["name"],
                    a_artists=self.parse_artists_list(item["artists"]),
                    a_album=item["album"]["name"],
                    a_uri=item["uri"],
                    a_duration_ms=item["duration_ms"],
                )

                if self.current_track is None:
                    self.current_track = t
                    self.last_track = t
                    last_track_db = self.get_last_activity_db()

                    print("Last entry on db: {}".format(last_track_db))
                    print("First song: {}".format(t))

                    if t != last_track_db:
                        print("Adding first song to db: {}".format(t))
                        self.record_activity(self.current_track, shuffle_state)
                    return True

                elif t == self.current_track:
                    print("Still playing {}".format(self.current_track))
                    return False

                else:
                    print("Previous song: {}".format(self.last_track))
                    self.last_track = self.current_track
                    self.current_track = t
                    print("Updated current song to: {}".format(self.current_track))
                    self.record_activity(self.current_track, shuffle_state)
                    return True

            else:
                print("Not playing any track!")
                return False

        except BaseException as e:
            print("Error getting current playback.")
            print("Error: {}".format(e))
            exit()

    # TODO: Improve
    def get_currently_playing(self):
        res = self.update_currently_playing()

        if res:
            return self.current_track

        else:
            return None

    def record_activity(self, a_track, a_shuffle_state):
        id = self.get_track_db_id(a_track)

        if id > 0 and id is not None:
            res = self.write_activity_to_db(id, a_shuffle_state)

        # TODO: Error handling
        else:
            res = False

        if res:
            print("Logged activity with track id {}".format(id))

    def get_track_db_id(self, a_track=None):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        id = 0

        # TODO: Add exception handler and else for invalid track
        if a_track is not None and a_track.uri is not None:
            query = "SELECT * FROM tracks WHERE uri = %s"
            cursor.execute(query, [a_track.uri])
            result = cursor.fetchall()  # TODO: Can this be replaced by fetchone?

            if result:
                if len(result) > 1:
                    print(
                        "WARNING: More than one entry for the same track {}".format(
                            a_track.title
                        )
                    )

                for track in result:
                    if id == 0:
                        id = track[0]
                        break

            cursor.close()
            conn.close()

            if id > 0:
                return id

            else:
                return self.write_track_to_db(a_track)

    def write_track_to_db(self, a_track=None):
        if a_track is not None:
            try:
                features = self.sp.audio_features(tracks=[a_track.uri])[0]

                a_track.set_audio_features(
                    a_acousticness=features["acousticness"],
                    a_danceability=features["danceability"],
                    a_energy=features["energy"],
                    a_instrumentalness=features["instrumentalness"],
                    a_musical_key=features["key"],
                    a_liveness=features["liveness"],
                    a_loudness=features["loudness"],
                    a_speechiness=features["speechiness"],
                    a_tempo=features["tempo"],
                    a_time_signature=features["time_signature"],
                    a_valence=features["valence"],
                )

                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                insert_query = """
                    INSERT INTO tracks (
                        track_title,
                        artists,
                        album,
                        duration_ms,
                        acousticness,
                        danceability,
                        energy,
                        instrumentalness,
                        musical_key,
                        liveness,
                        loudness,
                        speechiness,
                        tempo,
                        time_signature,
                        valence,
                        uri
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """
                data_to_insert = (
                    a_track.title,
                    a_track.artists,
                    a_track.album,
                    a_track.duration_ms,
                    a_track.acousticness,
                    a_track.danceability,
                    a_track.energy,
                    a_track.instrumentalness,
                    a_track.musical_key,
                    a_track.liveness,
                    a_track.loudness,
                    a_track.speechiness,
                    a_track.tempo,
                    a_track.time_signature,
                    a_track.valence,
                    a_track.uri,
                )

                cursor.execute(insert_query, data_to_insert)
                conn.commit()
                cursor.close()
                conn.close()

                id = cursor.lastrowid

                print("Saved track {} to tracks".format(a_track.title))
                return id

            except BaseException as e:
                print("Exception: {}".format(e))
                traceback.print_exc()
                return 0

        else:
            print("Nothing to write to DB!")
            return 0

    # TODO: Improve cursor and conn close reliability
    def write_activity_to_db(self, a_track_db_id, a_shuffle_state):
        if a_track_db_id > 0:
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                insert_query = "INSERT INTO listening_activity (user_id, track_id, shuffle_state) VALUES (%s, %s, %s)"

                data_to_insert = [self.get_user_db_id(), a_track_db_id, a_shuffle_state]

                cursor.execute(insert_query, data_to_insert)
                conn.commit()

                cursor.close()
                conn.close()

                return True

            except BaseException as e:
                print("Exception: {}".format(e))
                traceback.print_exc()
                return False

        else:
            print("Nothing to write to DB!")
            return False

    def get_entries_from_db(self):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM listening_activity")
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        cursor.close()
        conn.close()

    # TODO: Can this be achieved through cursor._last_insert_id?
    # TODO: Getting value from db schema is not consistent!
    def get_last_activity_db(self):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        t = None

        sql_query = "SELECT MAX(activity_id) FROM listening_activity;"

        cursor.execute(sql_query)
        result = cursor.fetchone()[0]

        if result:
            print("Result from max query: {}".format(result))
            last_id = result
            t = self.get_track_from_id(last_id)

        # else:
        #     print("Failed to get last listening id!")

        cursor.reset()
        cursor.close()
        conn.close()
        return t

    def get_track_from_id(self, a_db_id=0):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        try:
            if isinstance(a_db_id, int):
                if a_db_id > 0:
                    listening_query = (
                        "SELECT * FROM listening_activity WHERE activity_id = %s"
                    )
                    cursor.execute(listening_query, [a_db_id])
                    listening_result = cursor.fetchall()
                    track_id = listening_result[0][2]

                    if track_id > 0:
                        track_query = "SELECT * FROM tracks WHERE track_id = %s"
                        cursor.execute(track_query, [track_id])
                        track_result = cursor.fetchall()[0]

                        track = Track(
                            a_title=track_result[1],
                            a_artists=track_result[2],
                            a_album=track_result[3],
                            a_uri=track_result[-1],
                            a_duration_ms=track_result[4],
                        )

                        cursor.close()
                        conn.close()
                        return track

                cursor.close()
                conn.close()
                return None

            else:
                print("Invalid id!")

        except BaseException as e:
            print("Exception: {}".format(e))
            traceback.print_exc()
            cursor.close()
            conn.close()
            return None


if __name__ == "__main__":
    monitor = Monitor()

    while True:
        print("---")
        monitor.get_currently_playing()
        time.sleep(10)
