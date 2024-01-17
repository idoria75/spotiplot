import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yaml import safe_load

PATH_TO_KEYS = "/app/spotiplot.env"


class Authenticator:
    def __init__(self):
        print("Starting Spotiplot authenticator")
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

            print("ID: {}\n Secret: {}\n URI: {}".format(id, secret, uri))

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

        except BaseException as e:
            print("Failed to read user credentials. Error: {}".format(e))
            exit()

        res = self.sp.current_playback()
        print("Authentication succeeded")


if __name__ == "__main__":
    a = Authenticator()
