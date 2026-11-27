# SpeeduPy

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)

SpeeduPy is a performance optimization tool developed in Python. It utilizes an advanced **memoization** and **persistent caching** approach applied to pure functions, drastically accelerating the execution time of scientific and computation-intensive scripts.

---

## Key Features

* **Flexible Cache:** Results persist in files, SQLite, MySQL, MongoDB (documents or GridFS) or Redis, with an optional Memcached layer in memory.
* **Extreme Performance:** Implementation of ultra-fast hashing algorithms, ensuring instantaneous cache lookups and maximizing retrieval speed.
* **Execution Modes:** Support for different optimization and sampling strategies.
* **Disposable Servers:** The server backends can be tried with Docker, through [`compose.yaml`](compose.yaml).

---

## How to Install

SpeeduPy can be installed in two primary ways: via Docker commands, or directly on your host machine.

SpeeduPy runs on Python 3.11, on Linux, Windows and macOS. Other Python versions are not supported yet.

### 0. Clone or Download the Repository

Start by getting the SpeeduPy source code onto your local machine:

```bash
# Option 1: Clone using Git
$ git clone https://github.com/dew-uff/speedupy.git
$ cd speedupy

# Option 2: Download the ZIP and unpack it
```

### Option 1: Using Dockerfile (Recommended for Isolation)

You can build and run the development image directly using the `Dockerfile` provided in the project root.

> **Known problem:** `docker build` currently fails, because conda asks for the Anaconda Terms of Service ([#150](https://github.com/dew-uff/speedupy/issues/150)). Until it is fixed, use Option 2.

```bash
# 1. Build the Docker image
$ docker build -t speedupy-dev .

# 2. Run the image in the background (mapping the current project folder for code access)
#    (The exact run command might need adjustments based on port mapping and volumes)
$ docker run -d --name speedupy-container -v $(pwd):/app speedupy-dev

# 3. Start the container if it was stopped
$ docker start speedupy-container

# 4. Access the environment shell
$ docker exec -it speedupy-container /bin/bash
```

### Option 2: Host Machine (Manual Setup)

For direct host installation, install the required Python packages. The `file` and `sqlite` storages need nothing else.

```bash
# Install the Python dependencies
$ python3.11 -m pip install -r requirements.txt
```

The server storages and the Memcached memory architectures also need their server: install it with your system's package manager, or try it with Docker ([Trying the server backends with Docker](#trying-the-server-backends-with-docker)). The versions SpeeduPy is tested with are MySQL 9.0.1, MongoDB 6.0.16, Redis 7.4.0 and Memcached 1.6.18.

### Hashes

`-H/--hash` chooses the hash that identifies each function call in the cache. The default is `xxhash`.

| Hash | Kind |
| :--- | :--- |
| `xxhash` | Non-cryptographic. The default. |
| `md5` | From the Python standard library. |
| `murmur` | MurmurHash, non-cryptographic. |
| `meowhash` | Native library, x86_64 only. |
| `a5hash` | Native library. A research hash: see [`docs/native-hashes.md`](docs/native-hashes.md). |
| `museair` | Native library. A research hash: see [`docs/native-hashes.md`](docs/native-hashes.md). |

The native hashes (`a5hash`, `meowhash`, `museair`) come prebuilt in `native/lib/` for Linux x86_64 and aarch64, Windows x64, and macOS x86_64 and arm64, so a plain clone runs them with no compiler. MeowHash exists for x86_64 only; on any other platform the other hashes still work. To rebuild the binaries (a changed wrapper, source commit or platform), follow [`native/README.md`](native/README.md); the design is [`docs/native-hashes.md`](docs/native-hashes.md).

---

## How to Set Up and Use

This section guides you through preparing your Python scripts for acceleration and setting up the server environment they may need.

The experiment's directory holds your scripts and the SpeeduPy source code in a folder named `speedupy` (a clone, or a link to one). Run the commands below from that directory.

```text
my_experiment/
├── file_name.py
└── speedupy/
```

### 1. Starting Database Servers

Skip this step if your experiment uses the `file` or `sqlite` storage: they need no server.

For a server storage or a Memcached memory architecture, start the server it needs: your own installation, or a disposable one ([Trying the server backends with Docker](#trying-the-server-backends-with-docker)).

Inside the container of the `Dockerfile` (Option 1), a shell script starts the servers installed there. It needs the container's conda environment and `/app/dbs` folder, so it does not run on a host machine. It does not create the data folders of the servers ([#153](https://github.com/dew-uff/speedupy/issues/153)):

```bash
# Starts all configured database servers
$ ./speedupy_dev_env.sh start all

# Stops them
$ ./speedupy_dev_env.sh stop all
```

### 2. Adapting Your Scripts

Mark the pure functions you want to accelerate with **`@deterministic`**, and import it from `speedupy.speedupy`. The main script needs a function named `main`: setup adds **`@initialize_speedupy`** to it, with its import.

```python
from speedupy.speedupy import deterministic


@deterministic
def fibonacci(n):
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)


def main():
    print(fibonacci(30))


if __name__ == "__main__":
    main()
```

### 3. Experiment Setup

This step analyzes your code, injects the decorators and creates the necessary metadata (like function call graphs). It rewrites your scripts. It must be run after any modification to your experiment's source code, or when setting up for the first time.

```bash
# Replace file_name.py with the name of your main experiment file
$ python3.11 speedupy/setup_exp/setup.py file_name.py

# To prepare a server storage, name it with -s/--storage (default: file)
$ python3.11 speedupy/setup_exp/setup.py -s redis file_name.py
```

`-s/--storage` takes the same names as the execution option of the same name: `sqlite`, `redis`, `mongo`, `gridfs`, `mongo-file`, `mongo-gridfs`, `file` and `mysql`. Setup prepares only that storage and never touches the servers of the others, so it needs no server unless you choose one. On the first setup of a directory, it empties the server storage you choose (Redis, MongoDB) or recreates its database (MySQL), so do not point it at a server that holds data you need.

Run the experiment with the same storage you set up, passing `-s` to both commands: their defaults differ, `file` for setup and `sqlite` for execution ([#146](https://github.com/dew-uff/speedupy/issues/146)). The local SQLite file that setup always creates holds the function-call provenance whatever the storage.

---

## Running and Optimizing Experiments

You can control the entire caching mechanism, from the hashing algorithm to the storage backend, using command-line arguments.

### Execution Options

| Short Arg | Long Arg | Description | Accepted Values |
| :---: | :--- | :--- | :--- |
| `-h` | `--help` | Displays all available options. | |
| `-H` | `--hash` | Hash that identifies a function call (see [Hashes](#hashes)). Default: `xxhash`. | `xxhash`, `md5`, `murmur`, `meowhash`, `a5hash`, `museair` |
| `-s` | `--storage` | Persistence backend: files, SQLite, MySQL, Redis, or MongoDB (documents; GridFS; documents with large data in files or in GridFS). Default: `sqlite`. | `file`, `sqlite`, `mysql`, `redis`, `mongo`, `gridfs`, `mongo-file`, `mongo-gridfs` |
| | `--exec-mode` | Execution mode: `manual` (default) caches the `@deterministic` functions, `no-cache` caches nothing. The other three modes are experimental (beta): see [docs/experimental.md](docs/experimental.md). | `manual`, `no-cache`, `accurate`, `probabilistic-counting`, `probabilistic-error` |
| | `--retrieval-strategy` | How data is loaded to main memory: each call when needed, all of a function, or everything at the start. Default: `eager`. | `lazy`, `function`, `eager` |
| | `--retrieval-exec-mode` | Whether loading blocks the experiment. Default: `sequential`. `thread` is beta: see [docs/experimental.md](docs/experimental.md). | `sequential`, `thread` |
| | `--mem-arch` | Cache structure in main memory. The `memcached-*` values need a Memcached server (write-through, write-back). Default: `2-dict-fast`. | `0-dict`, `1-dict`, `2-dict`, `2-dict-fast`, `memcached-wt`, `memcached-wb` |
| | `--serializer` | Serializer that persists the data. Default: `cloudpickle`. | `pickle`, `cloudpickle` |
| `-mt` | `--min-exec-time-to-memoize` | Minimum time, in seconds, a call must take to be cached. Default: 0.01. | |
| | `--measure-time` | Prints the time the script took to execute. | |
| | `--profile` | Prints counters of calls and cache hits at the end. | |

### Usage Examples

**1. Running Without Cache (Baseline Measurement):**

```bash
# Measures the time baseline, ignoring all cache settings
$ python3.11 file_name.py --exec-mode no-cache
```

**2. Running With Cache:**

```bash
# Example: MD5 hashing and SQLite storage
$ python3.11 speedupy/setup_exp/setup.py -s sqlite file_name.py
$ python3.11 file_name.py -H md5 -s sqlite
```

---

## Trying the server backends with Docker

You can try the server backends without installing a server: [`compose.yaml`](compose.yaml) starts disposable ones with Docker Compose. It is the file the tests of the server backends run against.

| To use | Profile | Port on this machine |
| :--- | :--- | :--- |
| `-s redis` | `redis` | 6379 |
| `-s mongo`, `-s gridfs`, `-s mongo-file`, `-s mongo-gridfs` | `mongo` | 27017 |
| `-s mysql` | `mysql` | 3306 |
| `--mem-arch memcached-wt` or `memcached-wb` | `memcached` | 11211 |

The profile `all` starts the four servers. From the experiment's directory, with the Python dependencies installed:

```bash
# 1. Start one server; the command returns when it is healthy
$ docker compose -f speedupy/compose.yaml --profile redis up -d --wait

# 2. Set up the experiment and run it with that storage
$ python3.11 speedupy/setup_exp/setup.py -s redis file_name.py
$ python3.11 file_name.py -s redis --profile

# 3. Remove the servers, and the cache with them
$ docker compose -f speedupy/compose.yaml --profile all down -v
```

These servers are for trying the backends:

* **They keep nothing.** The data lives in memory or in the container, and `down -v` removes it. For real use, install a server.
* **They have no password** (MySQL accepts `root` with an empty one) and listen on this machine's loopback only.
* **A port must be free.** Compose refuses to start when a server already holds it. Setup empties the storage it prepares, so never point it at a server that holds data you need.
* A script as small as the example above may run too fast to be cached: add `-mt 0` to cache every call.
* Setup does not empty Memcached ([#84](https://github.com/dew-uff/speedupy/issues/84)).

---

## Running Tests

How to set up the development environment and run the tests, with or without
database servers, is in [`CONTRIBUTING.md`](CONTRIBUTING.md#running-locally).
The tests that need a server erase its data, and are not run by default.

---
