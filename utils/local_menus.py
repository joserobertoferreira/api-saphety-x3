from enum import IntEnum


class SMTPPort(IntEnum):
    """
    Enum to represent SMTP ports.
    """

    SSL = 465
    TLS = 587


class TaxLevelCode(IntEnum):
    """
    Enum to represent tax level codes.
    """

    NOR = 23
    INT = 13
    RED = 6
    ISE = 0


class NoYes(IntEnum):
    """X3 local menu 1"""

    NO = 1
    YES = 2


class InvoiceStatus:
    """X3 local menu 418"""

    NOT_INVOICED = 1
    PARTLY_INVOICED = 2
    INVOICED = 3


class InvoiceType:
    """X3 local menu 645"""

    INVOICE = 1
    CREDIT_NOTE = 2
    DEBIT_NOTE = 3
    CREDIT_MEMO = 4
    PROFORMA = 5


class EntityType:
    # X3 local menu 943

    BUSINESS_PARTNER = 1
    COMPANY = 2
    SITE = 3
    USER = 4
    ACCOUNTS = 5
    LEADS = 6
    BUILDING = 7
    PLACE = 8
