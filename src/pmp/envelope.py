"""PMP Envelope — RFC 0 §3."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .naming import MESSAGE_TYPE_RE, sequence_hex


class Envelope(BaseModel):
    """The PMP Envelope, per RFC 0 §3.

    `sequence` MUST match the sequence component of the message's
    filename — enforcing that agreement is the spool layer's job
    (see `pmp.consumer.SpoolConsumer.claim_one`), not this model's.
    """

    model_config = ConfigDict(extra="forbid")

    pmp: str = "0.0"
    profile: str = "spool"
    message_type: str
    schema_version: int = Field(ge=1)
    created_at: datetime
    producer: str
    sequence: str
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("pmp")
    @classmethod
    def _check_pmp_version(cls, v: str) -> str:
        if v != "0.0":
            raise ValueError(f"unsupported pmp version {v!r}, expected '0.0'")
        return v

    @field_validator("profile")
    @classmethod
    def _check_profile(cls, v: str) -> str:
        if v != "spool":
            raise ValueError(f"unsupported profile {v!r}, expected 'spool'")
        return v

    @field_validator("message_type")
    @classmethod
    def _check_message_type(cls, v: str) -> str:
        if not MESSAGE_TYPE_RE.match(v):
            raise ValueError(
                f"message_type {v!r} does not match "
                r"[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*)+"
            )
        return v

    @field_validator("sequence")
    @classmethod
    def _check_sequence(cls, v: str) -> str:
        if v != v.lower():
            raise ValueError(f"sequence {v!r} must be lowercase hexadecimal")
        try:
            int(v, 16)
        except ValueError:
            raise ValueError(f"sequence {v!r} is not hexadecimal") from None
        return v

    @field_validator("created_at")
    @classmethod
    def _check_created_at_tz(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("created_at must be timezone-aware (UTC RFC 3339)")
        return v.astimezone(timezone.utc)

    @field_serializer("created_at")
    def _serialize_created_at(self, v: datetime) -> str:
        v = v.astimezone(timezone.utc)
        return v.strftime("%Y-%m-%dT%H:%M:%S.") + f"{v.microsecond // 1000:03d}Z"

    @classmethod
    def new(
        cls,
        *,
        message_type: str,
        producer: str,
        sequence: int,
        payload: dict[str, Any] | BaseModel,
        schema_version: int = 1,
    ) -> "Envelope":
        """Build an Envelope with `created_at` stamped as now (UTC)."""
        if isinstance(payload, BaseModel):
            payload = payload.model_dump(mode="json")
        return cls(
            message_type=message_type,
            schema_version=schema_version,
            created_at=datetime.now(timezone.utc),
            producer=producer,
            sequence=sequence_hex(sequence),
            payload=payload,
        )
