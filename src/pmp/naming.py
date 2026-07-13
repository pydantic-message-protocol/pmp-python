"""Filename format — RFC 0 §4.2."""

from __future__ import annotations

import re

from .exceptions import InvalidMessageTypeError

MESSAGE_TYPE_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*)+$")

_FILENAME_RE = re.compile(
    r"^(?P<sequence>[0-9a-f]+)-(?P<epoch_ms>[0-9a-f]+)-(?P<pid>[0-9a-f]+)\.pmp$"
)


def validate_message_type(message_type: str) -> None:
    """Raise InvalidMessageTypeError if message_type doesn't match the RFC 0 §3 grammar."""
    if not MESSAGE_TYPE_RE.match(message_type):
        raise InvalidMessageTypeError(
            f"message_type {message_type!r} does not match "
            r"[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*)+"
        )


def sequence_hex(sequence: int) -> str:
    """Render a sequence integer as lowercase hex with no 0x prefix."""
    return f"{sequence:x}"


def build_filename(sequence: int, epoch_ms: int, pid: int) -> str:
    """Build a `{sequence_hex}-{epoch_ms_hex}-{pid_hex}.pmp` filename (RFC 0 §4.2)."""
    return f"{sequence_hex(sequence)}-{epoch_ms:x}-{pid:x}.pmp"


def parse_filename(name: str) -> tuple[int, int, int]:
    """Parse a `.pmp` filename into (sequence, epoch_ms, pid), all as ints.

    Readers MUST parse the sequence numerically — lexical filename
    sorting is not a valid ordering (RFC 0 §4.2).
    """
    match = _FILENAME_RE.match(name)
    if not match:
        raise ValueError(f"{name!r} is not a valid PMP filename")
    return (
        int(match.group("sequence"), 16),
        int(match.group("epoch_ms"), 16),
        int(match.group("pid"), 16),
    )
