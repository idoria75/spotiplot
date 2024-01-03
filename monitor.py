import spotipy
from spotipy.oauth2 import SpotifyOAuth

from yaml import safe_load

PATH_TO_KEYS = '/usr/local/keys/spotiplot.env'

## TODO
## Store list of tracks
## Store number of times played
## Check if shuffle is on before storing new entries
## Store continuously
## Store songs played before and after an execution
## Count number of tracks played by a single artist
## Properly store tracks in a DB or log file (with parser)

class Track():
    def __init__(self, a_name='', a_artists=[]):
        self.name = a_name
        self.artists = ''
        if(a_artists):
            for i in range(len(a_artists) - 1):
                self.artists = self.artists + a_artists[i]['name'] + ', '
            self.artists = self.artists + a_artists[-1]['name']
        else:
            self.artists = 'invalid artist info'

    def __str__(self):
        return "{} by {}".format(self.name, self.artists)



class Monitor():

    def __init__(self):
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
                                        redirect_uri=uri)

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

        except BaseException as e:
            print("Failed to read user credentials. Error: ".format(e))
            exit()

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
        result = self.sp.current_playback()['item']
        t = Track(a_name=result['name'], a_artists=result['artists'])
        print("Currently playing: {}".format(t))

if __name__ == '__main__':
    monitor = Monitor()
    monitor.get_recently_played()
    print("---")
    monitor.get_currently_playing()
