import urllib.request
from http.client import HTTPResponse


# Ignores HTTP_PROXY and the other proxy variables: they may point to Burp,
# and adyn only talks to services on this computer.
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def open_direct(url: str, *, timeout: float) -> HTTPResponse:
    """Open `url` without going through any proxy."""
    response: HTTPResponse = _DIRECT.open(url, timeout=timeout)
    return response
