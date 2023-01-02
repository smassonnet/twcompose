<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/twcompose.svg?branch=main)](https://cirrus-ci.com/github/<USER>/twcompose)
[![ReadTheDocs](https://readthedocs.org/projects/twcompose/badge/?version=latest)](https://twcompose.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/twcompose/main.svg)](https://coveralls.io/r/<USER>/twcompose)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/twcompose.svg)](https://anaconda.org/conda-forge/twcompose)
[![Monthly Downloads](https://pepy.tech/badge/twcompose/month)](https://pepy.tech/project/twcompose)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/twcompose)
-->

# TwCompose

[![PyPI-Server](https://img.shields.io/pypi/v/twcompose.svg)](https://pypi.org/project/twcompose/)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

> CLI to manage rules and start tweets collection from the Twitter Stream API

With TwCompose, you can:

- Add, modify and delete Twitter stream rules in a simple configuration file
- Validate that your rules are properly format before applying your changes
- Get volume estimation for your rules to stay within the rate limits
- Start collecting tweets in the background (Docker) with error handling and restart mechanism

## Installation

Installing TwCompose requires at least Python 3.8

```shell
pip install twcompose
```

## Usage

### Create a credentials file

First, we need to specify the [Twitter authentication token](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api) to connect to the Twitter Stream API.
This needs to be specified in a YAML file (called `credentials.yml` by default) with the following format:

```yml
twitter_token: "<TWITTER_BEARER_TOKEN>"
```

### Create a Twitter-Compose file

The following is an example of a `twitter-compose.yml` file.
It defines stream parameters and rules as well as output driver to save collected tweets.

```yml
# twitter-compose.yml
image_tag: "0.1.0"

output:
  driver: local
  path: ./data/
  options:
    max_file_size: 1048576

parameters:
  tweet_fields:
    - text

streams:
  cop26:
    - tag: COP26GDA
      value: "#COP26GDA"
    - tag: bare cop26
      value: cop26 OR COP26 OR Cop26
```

#### Collection image reference

Controls the name and version of the Docker image used for the collector container.

```yml
# twitter-compose.yml
image_tag: "0.1.0"
image_name: "ghcr.io/smassonnet/twcollect"
```

#### Output driver reference

Controls how the collected tweets are being saved.
Only support saving to a local folder in gzip compressed JSONLines files.
Files are split according the `max_file_size` option.

```yml
# twitter-compose.yml
output:
  driver: local
  path: ./data/
  options:
    max_file_size: 1048576
```

##### `driver`

Only supports collection to a `local` folder.

##### `path`

Path to the local folder to save into.

##### `options`

- `max_file_size` (number of bytes): Tweets are written to a new file when the file size reaches that limit. Defaults to 1 Gb.

#### Stream parameters reference

Controls the fields collected from the tweets.

```yml
# twitter-compose.yml
parameters:
  tweet_fields:
    - text
```

See the [Twitter stream API reference](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream) for documentation.

Note that the following fields correspond to the Twitter fields ending with `.fields` instead of `_fields`:

- `media_fields`: `media.fields`
- `place_fields`: `place.fields`
- `poll_fields`: `poll.fields`
- `tweet_fields`: `tweet.fields`
- `user_fields`: `user.fields`

#### Stream rules reference

Defines the scope of tweet to collect. See [Twitter stream rules for reference](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules).

It is organised as a mapping between a stream group name (`cop26` is the example below) and a list of Twitter stream rules.
Naming the stream rules with unique and comprehensive tags is highly recommended.

```yml
# twitter-compose.yml
streams:
  cop26:
    - tag: COP26GDA
      value: "#COP26GDA"
    - tag: bare cop26
      value: cop26 OR COP26 OR Cop26
```

### Command-line inteface

Run `twitter-compose --help` from the command-line:

```
usage: twitter-compose [-h] [-f TC_FILE] [-p PROJECT_NAME]
                       [--credentials-file CREDENTIALS]
                       [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       {config,up,status,stop,volume} ...

Manage Twitter streams

positional arguments:
  {config,up,status,stop,volume}
    config              Show parsed configuration
    up                  Update Twitter streams
    status              Status of defined streams
    stop                Stop Twitter streams
    volume              Estimation of the monthly volume of streams

optional arguments:
  -h, --help            show this help message and exit
  -f TC_FILE, --file TC_FILE
                        The file name of the twitter-compose configuration
  -p PROJECT_NAME, --project-name PROJECT_NAME
                        Name of the current project
  --credentials-file CREDENTIALS, -c CREDENTIALS
                        A yaml file with mapping between credential name and
                        value
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level
```

#### `config`

Validates and prints the parsed `twitter-compose.yml` configuration.

#### `up`

Update twitter stream rules and starts/updates the local running stream collector Docker container.
If takes an optional `--check` argument to display the changes without running the update.

#### `status`

Show the installed Twitter stream rules and the status of the stream collector.

#### `stop`

Stop the Docker container running the collection.


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
