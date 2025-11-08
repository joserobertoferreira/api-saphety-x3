import datetime
from typing import TypedDict


class OrderReference(TypedDict):
    order_number: str
    order_date: datetime.date


class ControlArgs(TypedDict, total=False):
    invoice_number: str
    status: int
    filename: str
    message: str
    sended_at: datetime.date
    requestStatus: int
    requestId: str
    financialId: str


class SaphetyResponse(TypedDict):
    CorrelationId: str
    IsValid: bool
    Errors: list[str]
    Data: str | list[str]


class SaphetyResult(TypedDict):
    invoice_number: str
    response: SaphetyResponse
