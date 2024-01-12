# Spotiplot

A project for data analysis of Spotify usage.

## Python Requirements

```txt
spotipy==2.23.0
mysql-connector-python==8.2
pyyaml==6.0.1
```

## Docker environment

The app is launched through docker compose. This enables the Python service to start along with the database to store the listening data.

## Handling MySQL passwords

For the moment, an environment file is necessary. Copy the lines below into a new `.env` file:

```yaml
MYSQL_PASSWORD: sample_password
MYSQL_ROOT_PASSWORD: sample_root_password
```

## Handling Spotify credentials

Copy the lines below into a new `spotiplot.env` file inside the `app` folder:

```yaml
credentials:
    client_id: '<client_id>' 
    client_secret: '<client_secret>' 
    redirect_uri: '<redirect_uri>'

```

Populate the fields on this file with the information available on your [Spotify dashboard](https://developer.spotify.com/dashboard).

## Building the Docker Image

The docker image for the spotiplot monitor contains two scripts:

- One for authenticating with Spotify, generating the access tokens and storing them as cache inside the container.
- One for monitoring the songs that are played.

The image should be built and executed before the docker compose. This will allow the authentication procedure, which requires user input, to retrieve the necessary tokens.

```sh
cd <path_to_spotiplot>
docker build -t spotiplot_monitor app/.
docker run -it -p 8083:8083 -v $(pwd)/app/cache:/app/cache spotiplot_monitor
```

When the image is executed, it will provide an URL that should be copied into a browser. Authenticate with Spotify on this browser session, and then copy the resulting URL back into the docker container. This will store the necessary tokens.

Once the tokens are saved, it is possible to start the system through the command:

```sh
docker compose up
```

## Visualizing the data with Adminer

Adminer is included into the docker compose image to enable visualization of the content stored into the database (for debug purposes).

To log into Adminer:

- Make sure the docker compose environment is up.
- Go to the [adminer login page](http://<host_ip>:9090)
- Set server name to the MySQL service name `mysql`
- Set username to spotiplot
- Enter the password defined into the `MYSQL_PASSWORD` variable
