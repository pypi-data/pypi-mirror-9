"""Exceptions used by ``ImportConfig`` and it's subclasses."""


class ImportConfigError(Exception):

    """Base exception for ImportConfig."""


class InvalidFilePathError(ImportConfigError):

    """Exception to be thrown when an invalid filepath is passed."""
