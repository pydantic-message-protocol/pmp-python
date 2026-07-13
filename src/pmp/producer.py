"""Publication — RFC 0 §4.4."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .envelope import Envelope
from .exceptions import FilenameCollisionError
from .naming import build_filename
from .spool import Spool


class SpoolProducer:
    """Publishes PMP messages into a spool, per RFC 0 §4.4.

    Publication is atomic and durable: write to `tmp/`, fsync the
    file, atomically rename into `pending/`, fsync the destination
    directory.
    """

    def __init__(self, spool_dir: str | os.PathLike[str], producer_name: str) -> None:
        self.spool = Spool(spool_dir)
        self.spool.ensure_layout()
        self.producer_name = producer_name

    def emit(
        self,
        message_type: str,
        payload: dict[str, Any] | BaseModel,
        *,
        schema_version: int = 1,
    ) -> Path:
        """Build an envelope and publish it. Returns the final path in `pending/`."""
        sequence = self.spool.allocate_sequence()
        envelope = Envelope.new(
            message_type=message_type,
            producer=self.producer_name,
            sequence=sequence,
            payload=payload,
            schema_version=schema_version,
        )
        return self._publish(envelope, sequence)

    def _publish(self, envelope: Envelope, sequence: int) -> Path:
        epoch_ms = time.time_ns() // 1_000_000
        pid = os.getpid()
        filename = build_filename(sequence, epoch_ms, pid)

        tmp_path = self.spool.tmp / filename
        dest_path = self.spool.pending / filename

        if dest_path.exists():
            raise FilenameCollisionError(f"{dest_path} already exists")

        data = envelope.model_dump_json().encode("utf-8")

        try:
            fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            raise FilenameCollisionError(f"{tmp_path} already exists") from None
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)

        os.rename(tmp_path, dest_path)

        dir_fd = os.open(self.spool.pending, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

        return dest_path
