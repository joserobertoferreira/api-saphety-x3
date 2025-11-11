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


class HttpRequestType(IntEnum):
    """
    Enum to represent HTTP request types.
    """

    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4


# X3 Local Menus


class NoYes(IntEnum):
    """X3 local menu 1"""

    NO = 1
    YES = 2


class InvoiceOrigin(IntEnum):
    """X3 local menu 413"""

    DIRECT = 1
    ORDER = 2
    DELIVERY = 3
    INVOICE = 4
    QUOTATION = 5
    RETURN = 6
    SERVICE_CONTRACT = 7
    SERVICE_ORDER = 8
    TRANSFER = 9
    DUE_DATE = 10


class InvoiceStatus(IntEnum):
    """X3 local menu 418"""

    NOT_INVOICED = 1
    PARTLY_INVOICED = 2
    INVOICED = 3


class InvoiceType(IntEnum):
    """X3 local menu 645"""

    INVOICE = 1
    CREDIT_NOTE = 2
    DEBIT_NOTE = 3
    CREDIT_MEMO = 4
    PROFORMA = 5


class EntityType(IntEnum):
    # X3 local menu 943

    BUSINESS_PARTNER = 1
    COMPANY = 2
    SITE = 3
    USER = 4
    ACCOUNTS = 5
    LEADS = 6
    BUILDING = 7
    PLACE = 8


class SaphetyStatus(IntEnum):
    """X3 local menu 1000"""

    WAITING = 1
    SENT_SUCCESSFULLY = 2
    GENERATION_ERROR = 3
    SENT_ERROR = 4


class SaphetyIntegrationType(IntEnum):
    """X3 local menu 1001"""

    NO_INTEGRATION = 1
    CIUS_PT = 2
    PDF_SIGNATURE = 3
    PDF_RESENT = 4


class SaphetyRequestStatus(IntEnum):
    """X3 local menu 1002"""

    QUEUED = 1
    RUNNING = 2
    ERROR = 3
    FINISHED = 4


class SaphetyIntegrationStatus(IntEnum):
    """X3 local menu 1003"""

    NOT_INTEGRATED = 1
    NOT_SENT = 2
    ERROR = 3
    SENT = 4
    RECEIVED = 5
    REJECTED = 6
    PAID = 7


class SaphetyNotificationStatus(IntEnum):
    """X3 local menu 1004"""

    SENT = 1
    DELIVERED = 2
    READ = 3
    ERROR = 4
