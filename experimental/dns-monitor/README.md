# DNS Debugging Script

A flexible, asynchronous script for monitoring and debugging DNS resolution. It periodically sends DNS queries to specified domains, logging the response times, answers, and any errors. This is useful for identifying DNS slowness or intermittent resolution failures, especially within environments like Kubernetes.

## Features

- **Asynchronous Queries**: Leverages `asyncio` to perform non-blocking DNS lookups.
- **Concurrent Requests**: Can send multiple queries concurrently to simulate load.
- **Configurable Interval**: Runs checks at a defined interval.
- **Jitter**: Adds a random delay to requests to avoid thundering herd problems and simulate more realistic network conditions.
- **Custom DNS Server**: Option to target a specific upstream DNS server.
- **Flexible Configuration**: Can be configured via both command-line arguments and environment variables.

## Requirements

- Python 3.12+
- `uv` (for the recommended execution method)

## Installation

This script is designed to be run with `uv`, a next-generation Python package manager from Astral.

If you don't have `uv` installed, you can install it with one of the following commands:

**macOS and Linux:**
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For more installation options, please refer to the [official `uv` installation guide](https://astral.sh/uv#installation).

## Usage

The script is self-contained and includes its dependencies in the header.

### Recommended (with `uv`)

The easiest way to run the script is using `uv`, which will automatically create a virtual environment and install the required dependencies.

```sh
uv run --script dns_debugging.py -- [OPTIONS]
```

### Alternative (with `pip`)

If you prefer to use `pip`, you can set up a virtual environment manually.

1.  **Create and activate a virtual environment:**
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    On Windows, use `.venv\Scripts\activate`.

2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    ```sh
    python dns_debugging.py [OPTIONS]
    ```

## Configuration

The script can be configured using the following command-line options or their corresponding environment variables.

| Option                  | Environment Variable    | Default | Description                                                                  |
| ----------------------- | ----------------------- | ------- | ---------------------------------------------------------------------------- |
| `--domains`             | `TARGET_DOMAINS`        | N/A     | **Required.** Comma-separated list of domains to query.                        |
| `--dns-server`          | `DNS_SERVER`            | `None`  | Specific upstream DNS server IP to use. Defaults to system nameservers.      |
| `--interval`            | `CHECK_INTERVAL`        | `60`    | How often (in seconds) to run a batch of queries.                            |
| `--concurrent-requests` | `CONCURRENT_REQUESTS`   | `1`     | How many concurrent DNS requests to make for each domain.                    |
| `--jitter`              | `JITTER`                | `0.0`   | Introduce a random delay (jitter) to each request, up to this many seconds.  |
| `--timeout`             | `QUERY_TIMEOUT`         | `2.0`   | The amount of time (in seconds) to wait for a DNS response.                  |

## Example

Run DNS queries for `google.com` and `github.com` every 30 seconds, with 5 concurrent requests for each domain and a jitter of up to 0.5 seconds. The upstream DNS server at `8.8.8.8` will be used.

```sh
uv run --script dns_debugging.py \
  --domains "google.com,github.com" \
  --dns-server "8.8.8.8" \
  --interval 30 \
  --concurrent-requests 5 \
  --jitter 0.5
```

The same configuration using environment variables:

```sh
export TARGET_DOMAINS="google.com,github.com"
export DNS_SERVER="8.8.8.8"
export CHECK_INTERVAL=30
export CONCURRENT_REQUESTS=5
export JITTER=0.5

uv run --script dns_debugging.py
```

