import pytest

from pmp.exceptions import InvalidMessageTypeError
from pmp.naming import build_filename, parse_filename, sequence_hex, validate_message_type


def test_sequence_hex_no_prefix():
    assert sequence_hex(0) == "0"
    assert sequence_hex(42) == "2a"


def test_build_and_parse_filename_round_trip():
    name = build_filename(sequence=42, epoch_ms=0x197F50A74C8, pid=0x9C4)
    assert name == "2a-197f50a74c8-9c4.pmp"
    assert parse_filename(name) == (42, 0x197F50A74C8, 0x9C4)


def test_parse_filename_rejects_malformed_name():
    with pytest.raises(ValueError):
        parse_filename("not-a-pmp-file.txt")


@pytest.mark.parametrize(
    "message_type",
    ["build.completed", "repository.sync.requested", "a.b.c"],
)
def test_validate_message_type_accepts_valid(message_type):
    validate_message_type(message_type)  # should not raise


@pytest.mark.parametrize(
    "message_type",
    ["BuildCompleted", "build", "my_project.messages.BuildCompleted", ".leading", "trailing."],
)
def test_validate_message_type_rejects_invalid(message_type):
    with pytest.raises(InvalidMessageTypeError):
        validate_message_type(message_type)
