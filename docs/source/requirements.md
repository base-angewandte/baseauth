# System requirements

In order to install _baseauth_, you need to make sure to have the following set up:

- [Docker](https://docs.docker.com/get-docker/)
  - make sure you also have the compose plugin there (should be given for any new docker
    install). It suffices to install the docker engine (especially if you are working on
    a server). If you want to have a nice GUI overview on your local developer machine,
    choose the Docker Desktop version for your system.
- The `build-essential` package (in Debian-based Linux distributions), to run the
  `make` command.

For production systems you will also need a web server, acting as a proxy and handling
incoming TLS connections and the needed certificates for those. We suggest to use
[nginx](https://www.nginx.com/).

If you want to actively develop or run a development instance directly on your
host (aka _the full developer setup_), you will also need:

- Dev libraries for: `libldap2-dev libsasl2-dev libssl-dev`
- The latest [Python 3](https://www.python.org/) version and [pyenv](https://github.com/pyenv/pyenv)
