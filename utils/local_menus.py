from enum import IntEnum


class SMTPPort(IntEnum):
    """
    Enum to represent SMTP ports.
    """

    SSL = 465
    TLS = 587


class NoYes(IntEnum):
    """Local Menu X3"""

    NO = 1
    YES = 2
