"""The one error the server backends raise when their server cannot be used."""

from typing import Optional


class ServerUnreachableError(ConnectionError):
    """The storage's server did not answer the probe made at construction."""


def server_unreachable(
    backend: str,
    server: str,
    address: str,
    install_url: str,
    profile: str,
    detail: Optional[str] = None,
) -> ServerUnreachableError:
    """Build the error, in the style of the missing-driver message.

    ``detail`` is the driver's own text, for a backend whose failure may be
    something other than an unreachable server (MySQL: a refused login).
    """
    message = (
        f"The {backend} backend needs a {server} server at {address}, "
        "which is not reachable.\n"
        f"You can: install {server} on this machine (see {install_url});\n"
        "start a disposable one with Docker "
        f"(docker compose --profile {profile} up -d --wait, see README);\n"
        "or choose a storage that needs no server (-s file or -s sqlite)."
    )
    if detail:
        message += f"\nThe driver said: {detail}"
    return ServerUnreachableError(message)
