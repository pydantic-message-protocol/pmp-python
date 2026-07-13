"""Exceptions for the PMP reference implementation."""


class PMPError(Exception):
    """Base class for all PMP errors."""


class InvalidMessageTypeError(PMPError):
    """Raised when a message_type does not match the RFC 0 §3 grammar."""


class SequenceMismatchError(PMPError):
    """Raised when a filename's sequence disagrees with the envelope's sequence field."""


class FilenameCollisionError(PMPError):
    """Raised when publishing would overwrite an existing destination file."""


class SpoolLayoutError(PMPError):
    """Raised when a spool directory's lifecycle layout is missing or malformed."""
