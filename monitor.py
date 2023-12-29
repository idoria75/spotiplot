import spotipy
from spotipy.oauth2 import SpotifyOAuth

from yaml import safe_load

PATH_TO_KEYS = '/usr/local/keys/spotiplot.env'


class Monitor():

    def __init__(self):
        self.authenticate()

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
                                        redirect_uri=uri)

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

        except BaseException as e:
            print("Failed to read user credentials. Error: ".format(e))
            exit()

    def get_recently_played(self):
        res_list = self.sp.current_user_recently_played(limit=50)
        items = res_list['items']

        tracks = []

        for j in range(len(items)):
            name = items[j]['track']['name']
            artists = []
            for i in range(len(items[j]['track']['artists'])):
                artists.append(items[j]['track']['artists'][i]['name'])
            tracks.append((name, artists))

        print(tracks)

        # Get before and after unix timestamps
        cursors = res_list['cursors']
        print(cursors)

    def get_currently_playing(self):
        results = self.sp.current_playback()['item']['name']
        if (results is not None):
            print(results)


if __name__ == '__main__':
    monitor = Monitor()
    monitor.get_recently_played()
    monitor.get_currently_playing()
