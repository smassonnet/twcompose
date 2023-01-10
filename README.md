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

TwCompose requires at least Python 3.8 and an instance running Docker.

```shell
pip install twcompose
```

## Getting started

This section is a step by step guide to create a first collection of tweets from the Twitter Filtered Stream API.

First, we need to create a credentials file to specify the [Twitter authentication token](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).
This needs to be done in a YAML file (called `credentials.yml` by default) with the following format:

```yml
# credentials.yml
twitter_token: "<TWITTER_BEARER_TOKEN>"
```

Then, we need to configure TwCompose in a file called `twitter-compose.yml`.
This file contains the definition of:

- **Stream rules**: Defines the scope of tweets to collect (see the Twitter guide on [how to build a rule][tw-build-rule])
- **Parameters**: Defines the tweets' attributes to collect from the filtered stream API (see the [Filtered Stream documentation][tw-get-filtered-stream])
- **Collection and output files**: Defines which version of the collection script ([TwCollect][twcollect]) to use as well as the output path parameters.

This is an example of file that collects tweet text for tweets mentioning the `chocolate` with an image attached.

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
  chocolate_images:
    - tag: chocolate_media
      value: chocolate has:media
```

Once defined, the stream collection can be validated and started with the following commands:

| Command                      | Description                                                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `twitter-compose up --check` | Validates the content of the rules against the Twitter API. This is a dry run command that will not perform and update. |
| `twitter-compose volume`     | Estimates the volume of each rule defined in the `streams` section.                                                     |
| `twitter-compose up`         | Starts the collection of tweets from the Filtered Stream API.                                                           |

## Twitter Compose file reference

The main configuration of TwCompose is done in the `twitter-compose.yml` file.
This section describes the configuration attributes of this file.

### `image_name`, `image_tag`

Controls the name and version of the Docker image used for the container collecting tweets.
By default, it uses the [TwCollect][twcollect] Docker image.

```yml
# twitter-compose.yml
image_tag: "0.1.0"
image_name: "ghcr.io/smassonnet/twcollect"
```

### `output`

Controls how the collected tweets are being saved.
Only support saving to a local folder in gzip compressed JSONLines files.
Files are split according the `max_file_size` option.
The following table describes the configuration keys supported by `output`

| Key                     | Type             | Description                                                                               |
| ----------------------- | ---------------- | ----------------------------------------------------------------------------------------- |
| `driver`                | `str`            | Only supports collection to a `local` folder.                                             |
| `path`                  | `str`            | Path to the local folder to save into.                                                    |
| `options.max_file_size` | `int` (in bytes) | Tweets are written to a new file when the file size reaches that limit. Defaults to 1 Gb. |

```yml
# twitter-compose.yml
output:
  driver: local
  path: ./data/
  options:
    max_file_size: 1048576
```


### `parameters`

Controls the tweet fields collected from the Filtered Stream API.
See the [Twitter stream API reference](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream) for documentation.

Note that the following fields correspond to the Twitter fields ending with `.fields` instead of `_fields`:

- `media_fields`: `media.fields`
- `place_fields`: `place.fields`
- `poll_fields`: `poll.fields`
- `tweet_fields`: `tweet.fields`
- `user_fields`: `user.fields`

```yml
# twitter-compose.yml
parameters:
  tweet_fields:
    - text
```


### `streams`

Defines the scope of tweet to collect. See [Twitter stream rules for reference](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules).

It is organised as a mapping between a stream group name (`cop26` in the example below) and a list of Twitter stream rules.
Naming the stream rules with unique and self-explanatory tags is highly recommended.

```yml
# twitter-compose.yml
streams:
  cop26:
    - tag: cop26-hashtags
      value: "#COP26"
```

## Command-line interface

Commands documentation can be printed using `twitter-compose --help`.
This section goes through all commands supported by the TwCompose CLI.

### `config`

Validates and prints the `twitter-compose.yml` configuration file.

### `up`

Update twitter stream rules and starts/updates the local running stream collector Docker container.
If takes an optional `--check` argument to display the changes without running the update.

### `status`

Show the installed Twitter stream rules and the status of the stream collector.

### `stop`

Stop the Docker container running the collection.


### `volume`

Prints an estimate of the number of tweets matching each rules defined in `streams` for a month.
It take an optional parameter `--min MIN_TWEET_COUNT` to only print rules with more that MIN_TWEET_COUNT tweets per month.
Rules can also be passed directly as positional arguments to the `volume` command to interactively test and build new rules:

```shell
twitter-compose volume "chocolate has:media"
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.


[tw-build-rule]: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
[tw-get-filtered-stream]: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream
[twcollect]: https://github.com/smassonnet/twcollect
