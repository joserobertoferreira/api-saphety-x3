import datetime
import decimal
from typing import TYPE_CHECKING, ClassVar

from sqlalchemy import DateTime, Index, Integer, LargeBinary, Numeric, PrimaryKeyConstraint, SmallInteger, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import DATABASE, DB_COLLATION, DEFAULT_LEGACY_DATE
from database.base import Base

from .generics_mixins import ArrayColumnMixin
from .mixins import AuditMixin, CreateUpdateDateMixin, DimensionMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from .address import Address


class Company(Base, AuditMixin, PrimaryKeyMixin, ArrayColumnMixin, DimensionMixin, CreateUpdateDateMixin):
    __tablename__ = 'COMPANY'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='COMPANY_ROWID'),
        Index('COMPANY_CPY0', 'CPY_0', unique=True),
        Index('COMPANY_CPY1', 'LEG_0', 'CPY_0'),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    companyName: Mapped[str] = mapped_column('CPYNAM_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    shortTitle: Mapped[str] = mapped_column('CPYSHO_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    isLegalCompany: Mapped[int] = mapped_column('CPYLEGFLG_0', TINYINT, default=text('((2))'))
    legislation: Mapped[str] = mapped_column('LEG_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    accountingModel: Mapped[str] = mapped_column('ACM_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    mainSite: Mapped[str] = mapped_column('MAIFCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    country: Mapped[str] = mapped_column('CRY_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    sirenNumber: Mapped[str] = mapped_column('CRN_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    sicCode: Mapped[str] = mapped_column('NAF_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    uniqueIdentificationNumber: Mapped[str] = mapped_column(
        'NID_0', Unicode(80, collation=DB_COLLATION), default=text("''")
    )
    legalForm: Mapped[str] = mapped_column('CPYLOG_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    registeredCapital: Mapped[decimal.Decimal] = mapped_column('RGCAMT_0', Numeric(20, 5), default=text('((0))'))
    registeredCapitalCurrency: Mapped[str] = mapped_column(
        'RGCCUR_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    defaultAddress: Mapped[str] = mapped_column('BPAADD_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    contactName: Mapped[str] = mapped_column('CNTNAM_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    bankNumber: Mapped[str] = mapped_column('BIDNUM_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    accountingCode: Mapped[str] = mapped_column('ACCCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    divisionCode: Mapped[str] = mapped_column('DIVCOD_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    intraCommunityVatNumber: Mapped[str] = mapped_column(
        'EECNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    x3Folder: Mapped[str] = mapped_column('FDRX3_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    firstFiscalYear: Mapped[datetime.datetime] = mapped_column('STRPER_0', DateTime, default=DEFAULT_LEGACY_DATE)
    accountingCurrency: Mapped[str] = mapped_column('ACCCUR_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    portugueseCompanyActivity: Mapped[str] = mapped_column(
        'KACT_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    additionalNumber: Mapped[int] = mapped_column('NUMADD_0', SmallInteger, default=text('((0))'))
    originsAutoCertification: Mapped[int] = mapped_column('ORICERFLG_0', TINYINT, default=text('((0))'))
    eoriNumber: Mapped[str] = mapped_column('EORINUM_0', Unicode(35, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='OBYDIE',
        property_name='mandatory_dim',
        count=20,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    isMandatoryDimensions = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    rexNumber: Mapped[str] = mapped_column('REXNUM_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    federalState: Mapped[str] = mapped_column('STAFED_0', Unicode(1, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DACDIE',
        property_name='enter_dim',
        count=20,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    enterDimensionsAscending = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    consolidation: Mapped[str] = mapped_column('GRUCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    codeStructure: Mapped[str] = mapped_column('PLISTC_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    retained: Mapped[int] = mapped_column('RTZFLG_0', SmallInteger, default=text('((0))'))
    collectionAgent: Mapped[int] = mapped_column('AGTPCP_0', SmallInteger, default=text('((0))'))
    taxRules: Mapped[str] = mapped_column('VACCPY_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    directReportSite: Mapped[int] = mapped_column('DCLDIRBALPAY_0', TINYINT, default=text('((0))'))
    economicReason: Mapped[str] = mapped_column('BDFECOCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    financialDepartment: Mapped[str] = mapped_column(
        'AUSFINSRV_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    defaultValue: Mapped[int] = mapped_column('GERDEFVAL_0', SmallInteger, default=text('((0))'))
    taxNumber: Mapped[str] = mapped_column('GEREECNUM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    taxCenter: Mapped[str] = mapped_column('GERTAXCEN_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    taxIdentifier: Mapped[str] = mapped_column('GERTAXIDT_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    elmasSenderID: Mapped[str] = mapped_column('GERCODELMA5_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    participantCode: Mapped[str] = mapped_column('GERPTP_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    customerThresholdInCash: Mapped[decimal.Decimal] = mapped_column(
        'SPABPCTSD_0', Numeric(28, 8), default=text('((0))')
    )
    supplierThresholdInCash: Mapped[decimal.Decimal] = mapped_column(
        'SPABPSTSD_0', Numeric(28, 8), default=text('((0))')
    )
    yearlyThreshold: Mapped[decimal.Decimal] = mapped_column('SPAYEATSD_0', Numeric(28, 8), default=text('((0))'))
    certifiedExpert: Mapped[str] = mapped_column('PORCTFACN_0', Unicode(9, collation=DB_COLLATION), default=text("''"))
    companyActivity: Mapped[str] = mapped_column('PORCPYACT_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    frequency: Mapped[int] = mapped_column('PORDCLPER_0', TINYINT, default=text('((0))'))
    legalRepresentative: Mapped[str] = mapped_column('PORLRC_0', Unicode(9, collation=DB_COLLATION), default=text("''"))
    headOffice: Mapped[int] = mapped_column('PORHQR_0', TINYINT, default=text('((0))'))
    detailedActivity: Mapped[str] = mapped_column(
        'PORCPYACTDET_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    financialDepartment1: Mapped[str] = mapped_column(
        'PORFINDPR_0', Unicode(9, collation=DB_COLLATION), default=text("''")
    )
    sepaCreditorIdentifier: Mapped[str] = mapped_column(
        'SCINUM_0', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    activityType: Mapped[int] = mapped_column('PORCPYACTTYP_0', TINYINT, default=text('((0))'))
    simplifiedInvoice: Mapped[int] = mapped_column('PORSIMINVISS_0', TINYINT, default=text('((0))'))
    simplifiedInvoiceSerie: Mapped[decimal.Decimal] = mapped_column(
        'PORAMTSERINV_0', Numeric(14, 3), default=text('((0))')
    )
    simplifiedInvoiceItem: Mapped[decimal.Decimal] = mapped_column(
        'PORAMTITMINV_0', Numeric(14, 3), default=text('((0))')
    )
    invoicingCompany: Mapped[str] = mapped_column(
        'PORRESFISCDA_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    activation: Mapped[int] = mapped_column('SSTTAXACT_0', SmallInteger, default=text('((0))'))
    sageSalesTaxCompany: Mapped[str] = mapped_column('SSTCPY_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    discountInvoicingElement: Mapped[int] = mapped_column('SFINUM_0', SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='COMMTYPE',
        property_name='communication_type',
        count=9,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    communication_types = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='STRDAT',
        property_name='start_date',
        count=9,
        column_type=DateTime,
        python_type=datetime.datetime,
        default=text(f"'{DEFAULT_LEGACY_DATE}'"),
    )

    start_dates = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='ENDDAT',
        property_name='end_date',
        count=9,
        column_type=DateTime,
        python_type=datetime.datetime,
        default=text(f"'{DEFAULT_LEGACY_DATE}'"),
    )

    end_dates = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    taxAgencyNumber: Mapped[str] = mapped_column('TAXAGCNUM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    taxAgencyName: Mapped[str] = mapped_column('TAXAGCNAM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    taxAgentNumber: Mapped[str] = mapped_column('TAXAGNNUM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    taxAgentName: Mapped[str] = mapped_column('TAXAGNNAM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    arabicName: Mapped[str] = mapped_column('ARACPYNAM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    gosiReferenceNumber: Mapped[str] = mapped_column(
        'GOSIREFNUM_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    sector1: Mapped[str] = mapped_column('SCT1_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    sector2: Mapped[str] = mapped_column('SCT2_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    molEstablishmentID: Mapped[str] = mapped_column('MOLID_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    trCustomerReference: Mapped[str] = mapped_column('TRECPY_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    cdCustomerReference: Mapped[str] = mapped_column(
        'TRECPY2_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    installation: Mapped[int] = mapped_column('IMPCPY_0', SmallInteger, default=text('((0))'))
    wasteDBNumber: Mapped[str] = mapped_column('BDO_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    agreement: Mapped[str] = mapped_column('AGREEMENT_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    serviceID: Mapped[str] = mapped_column('SERVICEID_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    startPeriod: Mapped[datetime.datetime] = mapped_column('INIPER_0', DateTime, default=DEFAULT_LEGACY_DATE)
    endPeriod: Mapped[datetime.datetime] = mapped_column('FINPER_0', DateTime, default=DEFAULT_LEGACY_DATE)
    solutionFinancing: Mapped[str] = mapped_column('SOLFIN_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    financedAmount: Mapped[decimal.Decimal] = mapped_column('AMTFIN_0', Numeric(28, 8), default=text('((0))'))

    # Específicos MOP
    activityType: Mapped[int] = mapped_column('XP_ACTTYP_0', TINYINT, default=text('((0))'))
    companyBillingResponsible: Mapped[str] = mapped_column(
        'XPINVCPY_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    localization: Mapped[int] = mapped_column('XPTAXCRYR_0', TINYINT, default=text('((0))'))

    exportFile: Mapped[str] = mapped_column('ZFILE_0', Unicode(60, collation=DB_COLLATION), default=text("''"))
    financialServicesCode: Mapped[int] = mapped_column('ZCOD_0', SmallInteger, default=text('((0))'))
    caeCodeRevision2: Mapped[int] = mapped_column('ZCAE_0', Integer, default=text('((0))'))
    activityCode: Mapped[int] = mapped_column('ZCTA_0', SmallInteger, default=text('((0))'))
    vatNumberTOC: Mapped[str] = mapped_column('ZNIFTOC_0', Unicode(9, collation=DB_COLLATION), default=text("''"))
    vatNumberLegalRepresentative: Mapped[str] = mapped_column(
        'ZNIFRL_0', Unicode(9, collation=DB_COLLATION), default=text("''")
    )
    footNote: Mapped[bytes] = mapped_column('ZRODAPE_0', LargeBinary, default=text('((0))'))

    # Relacionamentos
    addresses: ClassVar[list['Address']] = []
