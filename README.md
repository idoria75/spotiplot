# spotiplot

A project for data analysis of Spotify usage

## Python Requirements

Spotipy
PyYAML

## Docker environment

The app is launched through docker compose. This enables the Python service to start along with the database to store the listening data.

## Handling MySQL passwords

For the moment, an environment file is necessary. Copy the lines below into a new `.env` file:

```txt
MYSQL_PASSWORD: sample_password
MYSQL_ROOT_PASSWORD: sample_root_password
```

## Visualizing the data with Adminer

Adminer is included into the docker compose image to enable visualization of the content stored into the database (for debug purposes).

To log into Adminer:

- Make sure the docker compose environment is up.
- Go to the [adminer login page](http://localhost:8080)
- Set server name to the MySQL service name `mysql`
- Set username to spotiplot
- Enter the password defined into the `MYSQL_PASSWORD` variable
