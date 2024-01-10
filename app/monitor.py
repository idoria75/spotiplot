import os
import time
import spotipy
import mysql.connector
from spotipy.oauth2 import SpotifyOAuth
from yaml import safe_load

PATH_TO_KEYS = '/app/spotiplot.env'

db_pass = os.getenv('MYSQL_PASSWORD')

db_config = {
    'user': 'spotiplot',
    'password': db_pass,
    'host': 'mysql',
    'port': 3306,
    'database': 'spotiplot'
}


class Track():
    def __init__(self, a_name='', a_artists=[]):
        self.name = a_name
        self.artists = ''
        if (a_artists):
            for i in range(len(a_artists) - 1):
                self.artists = self.artists + a_artists[i]['name'] + ', '
            self.artists = self.artists + a_artists[-1]['name']
        else:
            self.artists = 'invalid artist info'

    def __str__(self):
        return "{} by {}".format(self.name, self.artists)


class Monitor():

    def __init__(self):
        print("Starting monitor")
        self.authenticate()
        self.last_played = []

    def authenticate(self):
        try:
            with open(PATH_TO_KEYS, 'r') as file:
                vars = safe_load(file).get('credentials')
                id = vars.get('client_id')
                secret = vars.get('client_secret')
                uri = vars.get('redirect_uri')

            self.scope = scope = "user-read-playback-state, user-read-currently-playing, user-read-recently-played"

            auth_manager = SpotifyOAuth(scope=scope,
                                        client_id=id,
                                        client_secret=secret,
                                        redirect_uri=uri,
                                        open_browser=False,
                                        cache_path="cache/.cache")

            print("ID: {}\n, Secret: {}\n, URI: {}".format(id, secret, uri))

            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.sp.current_playback()

        except BaseException as e:
            print("Failed to read user credentials. Error: {}".format(e))
            exit()

        print("Authentication succeeded")

    def get_recently_played(self):
        res_list = self.sp.current_user_recently_played(limit=50)
        items = res_list['items']

        tracks = []

        for i in range(len(items)):
            tracks.append(Track(a_name=items[i]['track']['name'], a_artists=items[i]['track']['artists']))

        for track in tracks:
            print(track)

        # Get before and after unix timestamps
        # cursors = res_list['cursors']
        # print(cursors)

    def get_currently_playing(self):
        while True:
            try:
                result = self.sp.current_playback()
                if result is not None:
                    item = result['item']
                    t = Track(a_name=item['name'], a_artists=item['artists'])
                    print("---")
                    print("Currently playing: {}".format(t))
            except BaseException as e:
                print("Error getting current playback.")
                print("Error: {}".format(e))
            time.sleep(2)


if __name__ == '__main__':
    monitor = Monitor()
    monitor.get_recently_played()
    monitor.get_currently_playing()
