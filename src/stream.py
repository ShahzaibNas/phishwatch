"""Certificate Transparency stream client for PhishWatch.

Connects to a certstream-compatible websocket server and feeds
every domain seen in new certificates to a callback function.
Knows nothing about matching — that's the matcher's job.

We run our own local certstream-server-go instance because the
public Calidog server (wss://certstream.calidog.io/) is no longer
reliable. See NOTES.md for the full story.
"""

import certstream


def start_stream(on_domain, url: str = "ws://127.0.0.1:8080/"):
    """Blocking. Calls on_domain(domain_str) for every domain in
    every new certificate seen by the CT logs.

    Args:
        on_domain: callback function taking a single domain string.
        url: websocket URL of a certstream-compatible server.
             Defaults to our local certstream-server-go instance.

   The certstream library pings the server every 15s internally, which satisfies our local server's 60s ping requirement.
    """

    def _handle(message, context):
        if message.get("message_type") != "certificate_update":
            return
        domains = (
            message.get("data", {})
            .get("leaf_cert", {})
            .get("all_domains", [])
        )
        for d in domains:
            on_domain(d)

    certstream.listen_for_events(_handle, url=url)