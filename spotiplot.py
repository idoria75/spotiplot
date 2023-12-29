import spotipy
from spotipy.oauth2 import SpotifyOAuth

from yaml import safe_load

path = '/usr/local/keys/spotiplot.env'
try:
    with open(path,'r') as file:
        vars = safe_load(file).get('credentials')
        id = vars.get('client_id')
        secret = vars.get('client_secret')
        uri = vars.get('redirect_uri')

except BaseException as e:
    print("Failed to read user credentials. Error: ".format(e))
    exit()

scope = "user-read-playback-state, user-read-currently-playing, user-read-recently-played"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=id, client_secret=secret, redirect_uri=uri))

# results = sp.current_playback()['item']['name']
res_list = sp.current_user_recently_played(limit=50)

items = res_list['items']

# for track in res_list:
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