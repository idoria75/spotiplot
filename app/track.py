
class Track:
    def __init__(self, a_title="", a_artists="", a_album="", a_uri="", a_duration_ms=0):
        if a_uri == "":
            raise ValueError("URI cannot be None.")

        self.title = a_title
        self.artists = a_artists
        self.album = a_album
        self.uri = a_uri
        self.duration_ms = a_duration_ms
        self.acousticness = 0.0
        self.danceability = 0.0
        self.energy = 0.0
        self.instrumentalness = 0.0
        self.musical_key = 0
        self.liveness = 0
        self.loudness = 0
        self.speechiness = 0.0
        self.tempo = 0.0
        self.time_signature = 0
        self.valence = 0.0

    def __str__(self):
        return "{} by {}".format(self.title, self.artists)

    def __eq__(self, a_other):
        if a_other is not None:
            return self.uri == a_other.uri
        else:
            return False

    def set_audio_features(
        self,
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
    ):
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

