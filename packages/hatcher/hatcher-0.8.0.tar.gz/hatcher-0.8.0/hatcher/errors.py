class HatcherException(Exception):
    pass


class MissingFilenameError(HatcherException):
    pass


class MissingPlatformError(HatcherException):
    pass


class ChecksumMismatchError(HatcherException):
    pass
