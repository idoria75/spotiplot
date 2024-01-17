import os
import time
import spotipy
import mysql.connector
from spotipy.oauth2 import SpotifyOAuth
from yaml import safe_load
from mysql.connector import errorcode

PATH_TO_KEYS = "/app/spotiplot.env"

db_pass = os.getenv("MYSQL_PASSWORD")

db_config = {
    "user": "spotiplot",
    "password": db_pass,
    "host": "mysql",
    "port": 3306,
    "database": "spotiplot",
}


class Track:
    def __init__(
        self,
        a_title="",
        a_artists="",
        a_album="",
        a_duration_ms=0,
        a_acousticness=0.0,
        a_danceability=0.0,
        a_energy=0.0,
        a_instrumentalness=0.0,
        a_musical_key=0,
        a_liveness=0.0,
        a_loudness=0.0,
        a_speechiness=0.0,
        a_tempo=0.0,
        a_time_signature=0,
        a_valence=0.0,
        a_uri="",
    ):
        if a_uri == "":
            raise ValueError("URI cannot be None.")

        self.title = a_title
        self.artists = ""
        self.album = a_album
        self.duration_ms = a_duration_ms
        self.acousticness = a_acousticness
        self.danceability = a_danceability
        self.energy = a_energy
        self.instrumentalness = a_instrumentalness
        self.musical_key = a_musical_key
        self.liveness = a_liveness
        self.loudness = a_loudness
        self.speechiness = a_speechiness
        self.tempo = a_tempo
        self.time_signature = a_time_signature
        self.valence = a_valence
        self.uri = a_uri

        if a_artists:
            for i in range(len(a_artists) - 1):
                self.artists = self.artists + a_artists[i]["name"] + ", "
            self.artists = self.artists + a_artists[-1]["name"]
        else:
            self.artists = "invalid artist info"

    def __str__(self):
        return "{} by {} - URI: {}".format(self.title, self.artists, self.uri)

    def __eq__(self, a_other):
        if a_other is not None:
            return (
                self.title == a_other.title
                and self.artists == a_other.artists
                and self.album == a_other.album
            )
        else:
            return False

    def print_properties(self):
        print("Title: {}".format(self.title))
        print("Artists: {}".format(self.artists))
        print("Album: {}".format(self.album))
        print("Duration: {}".format(self.duration_ms))
        print("Acousticness: {}".format(self.acousticness))
        print("Danceability: {}".format(self.danceability))
        print("Energy: {}".format(self.energy))
        print("Instrumentalness: {}".format(self.instrumentalness))
        print("Musical Key: {}".format(self.musical_key))
        print("Liveness: {}".format(self.liveness))
        print("Loudness: {}".format(self.loudness))
        print("Speechiness: {}".format(self.speechiness))
        print("Tempo: {}".format(self.tempo))
        print("Time Signature: {}".format(self.time_signature))
        print("Valence: {}".format(self.valence))
        print("URI: {}".format(self.uri))


class Monitor:
    def __init__(self):
        print("Starting spotiplot monitor")
        # self.authenticate_db()
        self.authenticate_spotify()
        self.last_played = []
        self.current_track = None
        self.last_track = None

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
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)

            except BaseException as e:
                print("Exception: {}".format(e))

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
            # self.sp.current_playback()
            self.current_user = self.sp.current_user()["display_name"]

        except BaseException as e:
            print("Failed to read user credentials. Error: {}".format(e))
            exit()

        print("Authentication succeeded for user: {}".format(self.current_user))

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

        # Get before and after unix timestamps
        # cursors = res_list['cursors']
        # print(cursors)

    def update_currently_playing(self):
        try:
            result = self.sp.current_playback()
            if result is not None:
                item = result["item"]
                features = self.sp.audio_features(tracks=[item["uri"]])[0]

                t = Track(
                    a_title=item["name"],
                    a_artists=item["artists"],
                    a_album=item["album"]["name"],
                    a_uri=item["uri"],
                    a_duration_ms=item["duration_ms"],
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
                print("---")
                # print("Shuffle state: {}".format(result["shuffle_state"]))

                if self.current_track is None:
                    self.current_track = t
                    self.last_track = t
                    print("First song: {}".format(t))
                    return True
                elif t == self.current_track:
                    print("Still playing {}".format(self.current_track))
                    return False
                else:
                    print("Previous song: {}".format(self.last_track))
                    self.last_track = self.current_track
                    self.current_track = t
                    print("Updated current song to: {}".format(self.current_track))
                    return True
            else:
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

    def write_entry_to_db(self, a_track=None):
        if a_track is not None:
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                insert_query = "INSERT INTO listening_activity (track_title, artist, album) VALUES (%s, %s, %s)"
                data_to_insert = (a_track.name, a_track.artists, a_track.album)

                cursor.execute(insert_query, data_to_insert)
                conn.commit()

                cursor.close()
                conn.close()

                print("Wrote {} to db".format(a_track.name))
                return True

            except BaseException as e:
                print("Exception: {}".format(e))
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

    # def get_current_user_display_name(self):
    #     return


if __name__ == "__main__":
    monitor = Monitor()
    print("---")
    # monitor.get_currently_playing()
    # monitor.get_entries_from_db()

    while True:
        # monitor.write_entry_to_db(monitor.get_currently_playing())
        monitor.get_currently_playing()
        # if t is not None:
        #     print(t)
        time.sleep(5)
