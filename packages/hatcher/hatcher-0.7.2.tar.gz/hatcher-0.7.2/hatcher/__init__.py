try:  # pragma: no cover
    from ._version import full_version as __version__
except ImportError:  # pragma: no cover
    __version__ = "not-built"
