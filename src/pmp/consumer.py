"""Claiming and completion — RFC 0 §4.5-4.6."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable

from .envelope import Envelope
from .exceptions import SequenceMismatchError
from .naming import parse_filename, sequence_hex
from .spool import Spool

Handler = Callable[[Envelope], None]


class SpoolConsumer:
    """Claims and processes PMP messages from a spool, per RFC 0 §4.5-4.6.

    Crash recovery is manual in v0.0 (RFC 0 §4.7) — this class never
    moves anything out of `processing/` on its own except via
    `complete`/`fail`.
    """

    def __init__(self, spool_dir: str | os.PathLike[str]) -> None:
        self.spool = Spool(spool_dir)
        self.spool.ensure_layout()
        self._handlers: dict[str, Handler] = {}

    def handler(self, message_type: str) -> Callable[[Handler], Handler]:
        """Decorator registering a handler for a given message_type."""

        def register(func: Handler) -> Handler:
            self._handlers[message_type] = func
            return func

        return register

    def claim_one(self) -> tuple[Path, Envelope] | None:
        """Claim the oldest pending message by atomically moving it into `processing/`.

        Returns (path_in_processing, envelope), or None if `pending/`
        has nothing claimable. Ordering is by the numeric sequence in
        the filename, not lexical sort (RFC 0 §4.2).
        """
        candidates: list[tuple[int, Path]] = []
        for entry in self.spool.pending.iterdir():
            if not entry.name.endswith(".pmp"):
                continue
            try:
                sequence, _, _ = parse_filename(entry.name)
            except ValueError:
                continue
            candidates.append((sequence, entry))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0])
        sequence, path = candidates[0]

        dest = self.spool.processing / path.name
        try:
            os.rename(path, dest)
        except FileNotFoundError:
            # Another consumer claimed it first between listing and rename.
            return self.claim_one()

        envelope = Envelope.model_validate_json(dest.read_text())
        if envelope.sequence != sequence_hex(sequence):
            raise SequenceMismatchError(
                f"{dest.name}: filename sequence {sequence_hex(sequence)} "
                f"!= envelope sequence {envelope.sequence}"
            )
        return dest, envelope

    def complete(self, path: Path) -> None:
        """Move a message from `processing/` to `completed/` (RFC 0 §4.6)."""
        os.rename(path, self.spool.completed / path.name)

    def fail(self, path: Path) -> None:
        """Move a message from `processing/` to `failed/` (RFC 0 §4.6)."""
        os.rename(path, self.spool.failed / path.name)

    def dispatch(self, path: Path, envelope: Envelope) -> None:
        """Run the registered handler for envelope.message_type, then complete/fail.

        A message is successfully consumed only when the handler
        returns without error (RFC 0 §4.6). No registered handler
        counts as failure.
        """
        handler = self._handlers.get(envelope.message_type)
        if handler is None:
            self.fail(path)
            return
        try:
            handler(envelope)
        except Exception:
            self.fail(path)
            raise
        else:
            self.complete(path)

    def run(self, *, poll_interval: float = 0.5, iterations: int | None = None) -> None:
        """Poll `pending/` and dispatch claimed messages until stopped.

        `iterations`, if given, bounds the number of poll cycles
        (mainly so tests can run this without looping forever).
        """
        count = 0
        while iterations is None or count < iterations:
            claimed = self.claim_one()
            if claimed is not None:
                self.dispatch(*claimed)
            else:
                time.sleep(poll_interval)
            count += 1
