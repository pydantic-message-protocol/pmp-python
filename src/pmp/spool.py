"""Directory layout and sequence allocation — RFC 0 §4.1-4.3."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path

SPOOL_SUBDIRS = ("tmp", "pending", "processing", "completed", "failed")

SEQUENCE_FILENAME = ".sequence"


class Spool:
    """A PMP spool rooted at a directory, per RFC 0 §4.1.

    Exposes the five lifecycle directories (tmp/pending/processing/
    completed/failed) and serializes sequence allocation through an
    advisory lock on a shared `.sequence` file (RFC 0 §4.3), so
    multiple local producers can share one spool safely.
    """

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root)

    def ensure_layout(self) -> None:
        """Create the five lifecycle directories if they don't already exist."""
        for name in SPOOL_SUBDIRS:
            self.dir(name).mkdir(parents=True, exist_ok=True)

    def dir(self, name: str) -> Path:
        if name not in SPOOL_SUBDIRS:
            raise ValueError(f"{name!r} is not a spool lifecycle directory")
        return self.root / name

    @property
    def tmp(self) -> Path:
        return self.dir("tmp")

    @property
    def pending(self) -> Path:
        return self.dir("pending")

    @property
    def processing(self) -> Path:
        return self.dir("processing")

    @property
    def completed(self) -> Path:
        return self.dir("completed")

    @property
    def failed(self) -> Path:
        return self.dir("failed")

    def allocate_sequence(self) -> int:
        """Allocate the next sequence number (RFC 0 §4.3). Sequences start at 0."""
        self.root.mkdir(parents=True, exist_ok=True)
        seq_path = self.root / SEQUENCE_FILENAME
        fd = os.open(seq_path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                raw = os.read(fd, 64).decode().strip()
                allocated = int(raw, 16) if raw else 0
                os.lseek(fd, 0, os.SEEK_SET)
                os.ftruncate(fd, 0)
                os.write(fd, f"{allocated + 1:x}".encode())
                os.fsync(fd)
                return allocated
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
