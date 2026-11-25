# SpeeduPy

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

SpeeduPy is a performance optimization tool developed in Python. It utilizes an advanced **memoization** and **persistent caching** approach applied to pure functions, drastically accelerating the execution time of scientific and computation-intensive scripts.

---

## Key Features

* **Flexible Cache:** Support for various storage backends (SQLite, MySQL, MongoDB, and Redis) for result persistence.
* **Extreme Performance:** Implementation of ultra-fast hashing algorithms, ensuring instantaneous cache lookups and maximizing retrieval speed.
* **Execution Modes:** Support for different optimization and sampling strategies.
* **Setup/Cleanup Scripts:** Environment controlled via simple shell scripts (`./speedupy_dev_env.sh`).

---

## How to Install

SpeeduPy can be installed in two primary ways: via Docker commands, or directly on your host machine.

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

For direct host installation, you must first install the required Python packages and configure the database servers manually.

```bash
# 1. Install Python Dependencies
$ pip install -r requirements.txt

# 2. Install Database Servers
#    You must manually install and configure the desired servers (MySQL, MongoDB, Redis, etc.)
#    that your project is set up to use. Consult your system's package manager for installation details.
#    (e.g., MySQL 8.0, Redis 7.2, MongoDB 7.0)
```

### Native Hashes

The native hashes (`a5hash`, `meowhash`, `museair`) come prebuilt in `native/lib/` for Linux x86_64 and aarch64, Windows x64, and macOS x86_64 and arm64, so a plain clone runs them with no compiler. MeowHash exists for x86_64 only; on any other platform the other hashes still work. To rebuild the binaries (a changed wrapper, source commit or platform), follow [`native/README.md`](native/README.md); the design is [`docs/native-hashes.md`](docs/native-hashes.md).


---

## How to Set Up and Use

This section guides you through setting up the required server environment and preparing your Python scripts for acceleration.

### 1. Starting Database Servers

Skip this step if your experiment uses the `file` or `sqlite` storage: they need no server.

If it uses a server storage (MySQL, MongoDB, Redis), start the server it needs. The provided shell script starts them all:

```bash
# Starts all configured database servers
$ ./speedupy_dev_env.sh start all
```

### 2. Experiment Setup

This step analyzes your code to create the necessary metadata (like function call graphs). This must be run after any modification to your experiment's source code, or when setting up for the first time.

```bash
# Replace file_name.py with the name of your main experiment file
$ python3.10 speedupy/setup_exp/setup.py file_name.py

# To prepare a server storage, name it with -s/--storage (default: file)
$ python3.10 speedupy/setup_exp/setup.py -s redis file_name.py
```

`-s/--storage` takes the same names as the execution option of the same name: `sqlite`, `redis`, `mongo`, `gridfs`, `mongo-file`, `mongo-gridfs`, `file` and `mysql`. Setup prepares only that storage and never touches the servers of the others, so it needs no server unless you choose one. On the first setup of a directory, it empties the server storage you choose (Redis, MongoDB) or recreates its database (MySQL), so do not point it at a server that holds data you need.

Run the experiment with the same storage you set up, passing `-s` to both commands. The local SQLite file that setup always creates holds the function-call provenance whatever the storage.

### 3. Adapting Your Scripts

To allow SpeeduPy to **track, measure, and cache function calls**, apply the relevant decorators to your script.  
Use **`@initialize_speedupy`** on the program’s `main` function and **`@deterministic`** on the pure functions you want to accelerate.

---

## Running and Optimizing Experiments

You can control the entire caching mechanism — from the hashing algorithm to the storage backend — using command-line arguments.

### Execution Options

| Short Arg | Long Arg | Description | Example Values |
| :---: | :--- | :--- | :--- |
| `-h` | `--help` | Displays all available options. | N/A |
| `-H` | `--hash` | Defines the hashing algorithm. Uses [MeowHash fork](https://github.com/JoaoLopez/meow_hash) for MeowHash support.| `meowhash`, `md5`, `murmurhash`, `xxhash` |
| `-s` | `--storage` | Defines the persistence backend. | `sqlite`, `mongo`, `mysql`, `redis`, `filesystem` |
|  | `--exec-mode` | Defines the execution mode. The other three modes are experimental (beta): see [docs/experimental.md](docs/experimental.md). | `manual`, `no-cache` |
|  | `--retrieval-strategy` | Defines how data is loaded to main memory. | `lazy`, `function`, `eager` |
|  | `--mem-arch` | Defines cache structure in main memory. | `0-dict`, `1-dict`, `2-dict`, `2-dict-fast`, `memcached-wt`, `memcached-wb` |
|  | `--serializer` | Defines which serializer will be used to persist data. | `pickle`, `cloudpickle` |
|  | `--measure-time` | Automatically measures time spent to execute the script. |  |

### Usage Examples

**1. Running Without Cache (Baseline Measurement):**

```bash
# Measures the time baseline, ignoring all cache settings
$ python3.10 file_name.py --exec-mode no-cache
```

**2. Running With Cache (Max Performance):**

```bash
# Example: Use fast MD5 hashing and SQLite storage
$ python3.10 file_name.py -H md5 -s sqlite
```

**3. Stopping Servers:**

```bash
$ ./speedupy_dev_env.sh stop all
```

---

## Running Tests

How to set up the development environment and run the tests, with or without
database servers, is in [`CONTRIBUTING.md`](CONTRIBUTING.md#running-locally).
The tests that need a server erase its data, and are not run by default.

---
