import datetime
import decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.settings import DATABASE, DB_COLLATION, DEFAULT_LEGACY_DATE, DEFAULT_LEGACY_DATETIME
from database.base import Base

from .generics_mixins import ArrayColumnMixin
from .mixins import AuditMixin, CreateUpdateDateMixin, DimensionMixin, DimensionTypesMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from .business_partner import BusinessPartner


class Customer(
    Base,
    AuditMixin,
    PrimaryKeyMixin,
    DimensionTypesMixin,
    DimensionMixin,
    CreateUpdateDateMixin,
):
    __tablename__ = 'BPCUSTOMER'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='BPCUSTOMER_ROWID'),
        Index('BPCUSTOMER_BPC0', 'BPCNUM_0', unique=True),
        Index('BPCUSTOMER_BPC1', 'BPCNAM_0'),
        Index('BPCUSTOMER_ZBPC3', 'ZCODACES_0'),  # Específico MOP
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    customerCode: Mapped[str] = mapped_column('BPCNUM_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    customerName: Mapped[str] = mapped_column('BPCNAM_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    shortName: Mapped[str] = mapped_column('BPCSHO_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    category: Mapped[str] = mapped_column('BCGCOD_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    reminderGroup: Mapped[str] = mapped_column('GRP_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    customerType: Mapped[int] = mapped_column('BPCTYP_0', TINYINT, default=text('((1))'))
    billToCustomer: Mapped[str] = mapped_column('BPCINV_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    billToCustomerAddress: Mapped[str] = mapped_column(
        'BPAINV_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    payByCustomer: Mapped[str] = mapped_column('BPCPYR_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    payByCustomerAddress: Mapped[str] = mapped_column(
        'BPAPYR_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    groupCustomer: Mapped[str] = mapped_column('BPCGRU_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    riskCustomer: Mapped[str] = mapped_column('BPCRSK_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    defaultAddress: Mapped[str] = mapped_column('BPAADD_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    defaultShipToAddress: Mapped[str] = mapped_column(
        'BPDADD_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    defaultContactName: Mapped[str] = mapped_column('CNTNAM_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    isActive: Mapped[int] = mapped_column('BPCSTA_0', TINYINT, default=text('((2))'))
    isProspect: Mapped[int] = mapped_column('PPTFLG_0', TINYINT, default=text('((1))'))
    ourSupplierCode: Mapped[str] = mapped_column('BPCBPSNUM_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    factor: Mapped[str] = mapped_column('FCTNUM_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    customerCurrency: Mapped[str] = mapped_column('CUR_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    rateType: Mapped[int] = mapped_column('CHGTYP_0', TINYINT, default=text('((1))'))
    commissionCategory: Mapped[int] = mapped_column('COMCAT_0', TINYINT, default=text('((1))'))
    salesRep1: Mapped[str] = mapped_column('REP_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    salesRep2: Mapped[str] = mapped_column('REP_1', Unicode(15, collation=DB_COLLATION), default=text("''"))
    taxRule: Mapped[str] = mapped_column('VACBPR_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    exemptionTaxNumber: Mapped[str] = mapped_column('VATEXN_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    paymentTerm: Mapped[str] = mapped_column('PTE_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    freightInvoicing: Mapped[int] = mapped_column('FREINV_0', TINYINT)
    earlyDiscount: Mapped[str] = mapped_column('DEP_0', Unicode(5, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTAAMT',
        property_name='percentOrAmount',
        count=30,
        column_type=Numeric,
        column_args=(20, 5),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    percentageOrAmounts = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTA',
        property_name='invoicingElement',
        count=30,
        column_type=Numeric,
        python_type=SmallInteger,
        server_default=text('((0))'),
    )

    invoicingElements = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TSCCOD',
        property_name='statisticGroup',
        count=5,
        column_type=Unicode,
        column_args=(20, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    statisticalGroups = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    priceType: Mapped[int] = mapped_column('PRITYP_0', TINYINT, default=text('((1))'))
    notes: Mapped[str] = mapped_column('BPCREM_0', Unicode(250, collation=DB_COLLATION), default=text("''"))
    creditControl: Mapped[int] = mapped_column('OSTCTL_0', TINYINT, default=text('((0))'))
    authorizedCredit: Mapped[decimal.Decimal] = mapped_column('OSTAUZ_0', Numeric(27, 13), default=text('((0))'))
    minimumOrderAmount: Mapped[decimal.Decimal] = mapped_column('ORDMINAMT_0', Numeric(27, 13), default=text('((0))'))
    creditInsurance: Mapped[decimal.Decimal] = mapped_column('CDTISR_0', Numeric(27, 13), default=text('((0))'))
    insuranceDate: Mapped[datetime.datetime] = mapped_column(
        'CDTISRDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    insuranceCompany: Mapped[str] = mapped_column(
        'BPCCDTISR_0', Unicode(15, collation=DB_COLLATION), default=text("''")
    )
    reminderType: Mapped[int] = mapped_column('FUPTYP_0', TINYINT, default=text('((1))'))
    minimumReminderAmount: Mapped[decimal.Decimal] = mapped_column(
        'FUPMINAMT_0', Numeric(27, 13), default=text('((0))')
    )
    noteType: Mapped[int] = mapped_column('SOIPER_0', TINYINT, default=text('((1))'))
    paymentBank: Mapped[str] = mapped_column('PAYBAN_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    accountingCode: Mapped[str] = mapped_column('ACCCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    canBeMatched: Mapped[int] = mapped_column('MTCFLG_0', TINYINT, default=text('((1))'))
    orderText: Mapped[str] = mapped_column('ORDTEX_0', Unicode(17, collation=DB_COLLATION), default=text("''"))
    invoiceText: Mapped[str] = mapped_column('INVTEX_0', Unicode(17, collation=DB_COLLATION), default=text("''"))
    loanAuthorized: Mapped[int] = mapped_column('LNDAUZ_0', TINYINT, default=text('((0))'))
    printAcknowledgement: Mapped[int] = mapped_column('OCNFLG_0', TINYINT, default=text('((0))'))
    invoicePeriod: Mapped[int] = mapped_column('INVPER_0', TINYINT, default=text('((0))'))
    dueDateOrigin: Mapped[int] = mapped_column('DUDCLC_0', TINYINT, default=text('((0))'))
    isOrderClosingAllowed: Mapped[int] = mapped_column('ORDCLE_0', TINYINT, default=text('((0))'))
    mustContainOneOrderPerDelivery: Mapped[int] = mapped_column('ODL_0', TINYINT, default=text('((0))'))
    partialDelivery: Mapped[int] = mapped_column('DME_0', TINYINT, default=text('((0))'))
    invoiceMode: Mapped[int] = mapped_column('IME_0', TINYINT, default=text('((0))'))
    businessSector: Mapped[str] = mapped_column('BUS_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    prospectOrigin: Mapped[str] = mapped_column('ORIPPT_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    tokenCredit: Mapped[int] = mapped_column('PITCDT_0', Integer, default=text('((0))'))
    manualAdditionalToken: Mapped[int] = mapped_column('PITCPT_0', Integer, default=text('((0))'))
    totalTokenCredit: Mapped[int] = mapped_column('TOTPIT_0', Integer, default=text('((0))'))
    serviceContract: Mapped[str] = mapped_column('COTCHX_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    necessaryTokens: Mapped[int] = mapped_column('COTPITRQD_0', Integer, default=text('((0))'))
    firstContactDate: Mapped[datetime.datetime] = mapped_column(
        'CNTFIRDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    lastContactDate: Mapped[datetime.datetime] = mapped_column(
        'CNTLASDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    nextContactDate: Mapped[datetime.datetime] = mapped_column(
        'CNTNEXDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    lastContactType: Mapped[int] = mapped_column('CNTLASTYP_0', TINYINT, default=text('((1))'))
    nextContactType: Mapped[int] = mapped_column('CNTNEXTYP_0', TINYINT, default=text('((1))'))
    firstOrderDate: Mapped[datetime.datetime] = mapped_column(
        'ORDFIRDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    lastQuoteDate: Mapped[datetime.datetime] = mapped_column(
        'QUOLASDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    classABC: Mapped[int] = mapped_column('ABCCLS_0', TINYINT, default=text('((1))'))
    vatCollectionAgent: Mapped[int] = mapped_column('AGTPCP_0', TINYINT, default=text('((0))'))
    regionalTaxesAgent: Mapped[int] = mapped_column('AGTSATTAX_0', TINYINT, default=text('((0))'))
    provinceCode: Mapped[str] = mapped_column('SATTAX_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    collectionAgent: Mapped[int] = mapped_column('FLGSATTAX_0', TINYINT, default=text('((0))'))
    printTemplate: Mapped[str] = mapped_column('TPMCOD_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    accountStructure: Mapped[str] = mapped_column('DIA_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    customerSince: Mapped[datetime.datetime] = mapped_column(
        'BPCSNCDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    exportNumber: Mapped[int] = mapped_column('EXPNUM_0', Integer, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DAYMON',
        property_name='paymentDay',
        count=6,
        column_type=SmallInteger,
        python_type=int,
        server_default=text('((0))'),
    )

    paymentDays = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    unavailablePeriod: Mapped[str] = mapped_column('UVYCOD2_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    cashIsActive: Mapped[int] = mapped_column('CSHVATRGM_0', TINYINT, default=text('((0))'))
    vatStartDate: Mapped[datetime.datetime] = mapped_column(
        'VATSTRDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    vatEndDate: Mapped[datetime.datetime] = mapped_column(
        'VATENDDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    isSubjectToTax: Mapped[int] = mapped_column('BELVATSUB_0', TINYINT, default=text('((0))'))
    invoicingTerm: Mapped[str] = mapped_column('INVCND_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    isElectronicInvoice: Mapped[int] = mapped_column('ELECTINV_0', TINYINT, default=text('((0))'))
    contact: Mapped[str] = mapped_column('CNTEFAT_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    startDataElectronicInvoice: Mapped[datetime.datetime] = mapped_column(
        'STRDATEFAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    isElectronicInvoiceAllowed: Mapped[int] = mapped_column('AEIFLG_0', TINYINT, default=text('((0))'))

    # Específicos MOP
    numberOfCopiesReceived: Mapped[int] = mapped_column('COPREC_0', SmallInteger, default=text('((0))'))
    accessCode: Mapped[str] = mapped_column('ZCODACES_0', Unicode(10, collation=DB_COLLATION), default=text("''"))

    typeCustomer: Mapped[int] = mapped_column('XP_BPCTYP_0', TINYINT, default=text('((1))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='XPIVACFLG',
        property_name='vat_regime',
        count=9,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    VatRegimes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='XPSTRDAT',
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
        db_column_prefix='XPENDDAT',
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

    # Específicos CIUS
    ciusType: Mapped[int] = mapped_column('YCIUSTYP_0', TINYINT, default=text('((0))'))

    business_partner: Mapped['BusinessPartner'] = relationship(
        'BusinessPartner',
        primaryjoin='foreign(Customer.customerCode) == BusinessPartner.code',
        back_populates='customer',
        lazy='joined',
        viewonly=True,
        uselist=False,
    )
