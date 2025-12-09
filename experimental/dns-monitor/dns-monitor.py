import asyncio
import logging
import random
import time

import click
import dns.asyncresolver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dns_monitor")


async def query_dns(domain, dns_server, timeout):
    """
    Perform a single asynchronous DNS query.
    """

    resolver = dns.asyncresolver.Resolver()

    # Use the specified nameservers, otherwise fall back to the system-defined nameservers
    if dns_server:
        resolver.nameservers = [dns_server]

    start_time = time.time()

    try:
        answer = await resolver.resolve(domain, "A", lifetime=timeout)

        duration = (time.time() - start_time) * 1000
        ip_addresses = [r.to_text() for r in answer]

        logger.info(
            f"SUCCESS: Domain='{domain}' | Time(ms)={duration:.2f} | "
            # This default answer is ...verbose. If a more compact log message is desired,
            # replace this answer log statement with the one below it
            f"Answer={answer.response.to_text().replace('\n', ', ')} | "
            # f"Answer={', '.join(repr(i) for i in answer)} "
            f"Detail={ip_addresses}"
        )
    # Capture all DNS-related exceptions and log them
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            f"ERROR: Domain='{domain}' | Time(ms)={duration:.2f} | "
            f"Answer={type(e).__name__} | Detail={str(e)}"
        )


async def make_dns_requests(
    domains, dns_server, interval, concurrent_requests, timeout, jitter
):
    """
    The main async event loop.
    """
    logger.info("Starting DNS Monitor... 👀")

    domains_list = [d.strip() for d in domains.split(",") if d.strip()]
    target_name = dns_server if dns_server else "Using system default nameserver"

    logger.info(f"Target Domains: {','.join(domains_list)}")
    logger.info(f"Target Nameserver: {target_name}")
    logger.info(f"Concurrent Requests: {concurrent_requests} per domain")
    logger.info(f"Interval: {interval} seconds")
    logger.info(f"Timeout: {timeout} seconds")
    logger.info(f"Request Jitter: {jitter} seconds")

    async def query_with_jitter(domain, dns_server, timeout):
        """Adds a random delay before querying a DNS server.

        A useful test case for a DNS server is to make multiple simultaneous requests for the same domain as this
        more closely resembles real-world workload behavior. Rather than fire N requests for the same domain
        simultaneously, the jitter value introduces some variability in the timing of the request, in an attempt to
        more accurately reflect real-world conditions.
        """
        await asyncio.sleep(random.uniform(0, jitter))
        await query_dns(domain, dns_server, timeout)

    while True:
        tasks = []
        for domain in domains_list:
            for _ in range(concurrent_requests):
                if jitter > 0:
                    tasks.append(query_with_jitter(domain, dns_server, timeout))
                else:
                    tasks.append(query_dns(domain, dns_server, timeout))
        await asyncio.gather(*tasks)

        # Non-blocking sleep
        await asyncio.sleep(interval)


@click.command()
@click.option(
    "--domains",
    envvar="TARGET_DOMAINS",
    required=True,
    help="Comma-separated list of domains to query.",
)
@click.option(
    "--dns-server",
    envvar="DNS_SERVER",
    required=False,
    default=None,
    help="Specific upstream DNS server IP to use.",
)
@click.option(
    "--interval",
    envvar="CHECK_INTERVAL",
    default=60,
    type=int,
    help="How often to run in seconds.",
)
@click.option(
    "--concurrent-requests",
    envvar="CONCURRENT_REQUESTS",
    default=1,
    type=int,
    help="The number of concurrent DNS requests to make.",
)
@click.option(
    "--jitter",
    envvar="JITTER",
    default=0.0,
    type=float,
    help="Introduce a random delay (jitter) to each request, up to this many seconds.",
)
@click.option(
    "--timeout",
    envvar="QUERY_TIMEOUT",
    default=2.0,
    type=float,
    help="The amount of time to wait for a response from the upstream DNS server.",
)
def cli(domains, dns_server, interval, concurrent_requests, jitter, timeout):
    """
    DNS Monitor: An asynchronous tool for continuously querying DNS and logging responses.

    Query a list of specified domains at regular intervals, supporting concurrent requests
    and an optional jitter to spread out the query timings.

    Args:
        domains (str): Comma-separated list of domains to query.
        dns_server (str, optional): Specific upstream DNS server IP to use. Defaults to system-defined nameservers if None.
        interval (int): How often (in seconds) to run a batch of DNS queries.
        concurrent_requests (int): The number of concurrent DNS requests to make for each domain in each interval.
        jitter (float): The maximum number of seconds to introduce a random delay before each individual DNS request.
        This helps to prevent thundering herds and distribute the load. Defaults to 0.0 (no jitter).
        timeout (float): The amount of time (in seconds) to wait for a response from the upstream DNS server for a single query.
    """
    try:
        asyncio.run(
            make_dns_requests(
                domains, dns_server, interval, concurrent_requests, timeout, jitter
            )
        )
    except KeyboardInterrupt:
        logger.info("Stopping monitor... 🫡")


if __name__ == "__main__":
    cli()
