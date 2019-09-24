# Async Web Crawler

An async Python web crawler.

## Local environment

### Setup

In a virtual env:

```
pip install -r requirements.txt
```

(or `pip-sync` if you have `pip-tools`)

### Run crawler

`cd` to the root directory and:

```
./run_crawler.py https://github.com
```

### Run tests

`cd` to the root directory and:

```
./run_tests.sh
```

## Docker

Unfortunately, because of an issue with `aiohttp`/`python`, as mentioned [here](https://github.com/aio-libs/aiohttp/issues/3535), the code that is reponsible for making the get requests might fail on machines that do not have a Python version of 3.7.4 and higher. For taht case, I have included a docker file and some commands where that you can use to run the crawler and the tests inside docker, using a Python 3.8 image.

### Setup

1. Install [Docker](https://docs.docker.com/install/).
2. From the root directory, run:

```
docker build -t crawler .
```

### Run crawler

```
docker run crawler python run_crawler.py https://github.com
```

### Run tests

```
docker run crawler python -m pytest tests/
```

### ssh into the container

If you need to ssh into the container to check what is there, like the crawler resuls file, you can do:

```
docker run -it crawler /bin/sh
```
