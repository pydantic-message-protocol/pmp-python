from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from pmp.envelope import Envelope


def test_new_builds_valid_envelope():
    envelope = Envelope.new(
        message_type="build.completed",
        producer="repository-a",
        sequence=42,
        payload={"repository": "example", "successful": True},
    )
    assert envelope.pmp == "0.0"
    assert envelope.profile == "spool"
    assert envelope.sequence == "2a"
    assert envelope.schema_version == 1
    assert envelope.created_at.tzinfo is not None


def test_created_at_serializes_as_millisecond_rfc3339_z():
    envelope = Envelope.new(
        message_type="build.completed",
        producer="repository-a",
        sequence=0,
        payload={},
    )
    envelope.created_at = datetime(2026, 7, 10, 18, 42, 31, 123000, tzinfo=timezone.utc)
    assert envelope.model_dump(mode="json")["created_at"] == "2026-07-10T18:42:31.123Z"


def test_round_trip_through_json():
    original = Envelope.new(
        message_type="build.completed",
        producer="repository-a",
        sequence=42,
        payload={"repository": "example"},
    )
    restored = Envelope.model_validate_json(original.model_dump_json())
    # created_at is serialized at millisecond precision by design (RFC 0
    # §3), so compare re-serialized JSON rather than the Python objects,
    # which may still differ by sub-millisecond microseconds.
    assert restored.model_dump_json() == original.model_dump_json()


@pytest.mark.parametrize(
    "field, value",
    [
        ("pmp", "0.1"),
        ("profile", "http"),
        ("message_type", "BuildCompleted"),
        ("sequence", "2A"),
        ("sequence", "not-hex"),
    ],
)
def test_rejects_invalid_fields(field, value):
    kwargs = dict(
        pmp="0.0",
        profile="spool",
        message_type="build.completed",
        schema_version=1,
        created_at=datetime.now(timezone.utc),
        producer="repository-a",
        sequence="2a",
        payload={},
    )
    kwargs[field] = value
    with pytest.raises(ValidationError):
        Envelope(**kwargs)


def test_rejects_naive_created_at():
    with pytest.raises(ValidationError):
        Envelope(
            message_type="build.completed",
            schema_version=1,
            created_at=datetime(2026, 7, 10, 18, 42, 31),
            producer="repository-a",
            sequence="2a",
            payload={},
        )


def test_rejects_extra_fields():
    with pytest.raises(ValidationError):
        Envelope(
            message_type="build.completed",
            schema_version=1,
            created_at=datetime.now(timezone.utc),
            producer="repository-a",
            sequence="2a",
            payload={},
            unexpected="field",
        )
