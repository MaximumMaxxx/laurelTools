# Laurel Tools
#### The 0 BS tools to get the job done.
[Current publicly hosted instance](https://tools.laurel.community)

## Features
- Youtube downloader
  - Audio and video

## todo
- [ ] Make the home page look nice
- [ ] Add a format dropdown for the youtube downloader
- [ ] Add a url shortener
- [ ] Add a pastebin type thing

## Depolying
The only prerequisite to deploy this is docker, docker-compose, and a laureltools_env secret.

Make a copy of the `.env.example` file called `stack.env` and fill in the values.

Then all you have to do is run the docker-compose file
```bash
docker-compose up -d
```

the container will run on port 5000 by default and should have some basic traeffik config to make it work with a reverse proxy automatically. Although you'll have to change it a little bit. Feel free to ignore the `labels` if you don't know what traefik is/don't use it.
