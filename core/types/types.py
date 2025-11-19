import datetime
from typing import Any, TypedDict


class OrderReference(TypedDict):
    order_number: str
    order_date: datetime.date


class InvoiceXmlData(TypedDict):
    invoice_number: str
    company: str
    site: str
    invoice_date: datetime.date


class ControlArgs(TypedDict, total=False):
    invoice_number: str
    status: int
    filename: str
    message: str
    sendDate: datetime.date
    requestStatus: int
    integrationStatus: int
    notificationStatus: int
    requestId: str
    financialId: str


class SaphetyResponse(TypedDict):
    CorrelationId: str
    IsValid: bool
    Errors: list[str]
    Data: str | dict[str, Any]


class SaphetyResult(TypedDict):
    invoice_number: str
    response: SaphetyResponse


class SaphetyIntegrationData(TypedDict, total=False):
    Id: str
    VirtualOperatorCode: str | None
    CompanyIntlVatCode: str
    DocumentType: str
    DocumentDate: str
    DocumentNumber: str
    ReceiverIntlVatCode: str
    ReceiverName: str
    DocumentStatus: str
    DocumentSource: str
    DocumentLink: str
    DocumentTotal: float
    CurrencyCode: str
    NotificationStatus: str
    IntegrationStatus: str
    IntegrationDate: str
    LastUpdateDate: str
    AuthorId: str
    Errors: list[str] | None
    CreationDate: str


class SaphetyIntegrationResponse(TypedDict):
    CorrelationId: str
    IsValid: bool
    Errors: list[str]
    Data: SaphetyIntegrationData


class SaphetyIntegrationResult(TypedDict):
    invoice_number: str
    response: SaphetyIntegrationResponse
