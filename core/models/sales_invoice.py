import datetime
import decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config.settings import DATABASE, DB_COLLATION, DEFAULT_LEGACY_DATETIME
from core.database.base import Base

from .generics_mixins import ArrayColumnMixin
from .mixins import AuditMixin, CreateUpdateDateMixin, DimensionMixin, DimensionTypesMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from .customer import Customer
    from .saphety_control import SaphetyApiControl


class CustomerInvoiceHeader(
    Base, AuditMixin, PrimaryKeyMixin, CreateUpdateDateMixin, DimensionTypesMixin, DimensionMixin
):
    __tablename__ = 'SINVOICE'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='SINVOICE_ROWID'),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    invoiceType: Mapped[str] = mapped_column('SIVTYP_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    category: Mapped[int] = mapped_column('INVTYP_0', TINYINT, default=text('((0))'))
    invoiceNumber: Mapped[str] = mapped_column('NUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    sourceModule: Mapped[int] = mapped_column('ORIMOD_0', TINYINT, default=text('((0))'))
    businessPartner: Mapped[str] = mapped_column('BPR_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    collective: Mapped[str] = mapped_column('BPRSAC_0', Unicode(12, collation=DB_COLLATION), default=text("''"))
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    site: Mapped[str] = mapped_column('FCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    entryType: Mapped[str] = mapped_column('GTE_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    journal: Mapped[str] = mapped_column('JOU_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    accountingDate: Mapped[datetime.datetime] = mapped_column('ACCDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    internalNumber: Mapped[int] = mapped_column('ACCNUM_0', Integer, default=text('((0))'))
    sourceDocumentDate: Mapped[datetime.datetime] = mapped_column('BPRDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    sourceDocument: Mapped[str] = mapped_column('BPRVCR_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    currency: Mapped[str] = mapped_column('CUR_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    rateType: Mapped[int] = mapped_column('CURTYP_0', TINYINT, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='LED',
        property_name='ledger',
        count=10,
        column_type=Unicode,
        column_args=(3, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    ledgers = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='CURLED',
        property_name='currency_ledger',
        count=10,
        column_type=Unicode,
        column_args=(3, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    currencyLedgers = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='RATMLT',
        property_name='rate_multiplier',
        count=10,
        column_type=Numeric,
        column_args=(21, 10),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    rateMultipliers = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='RATDIV',
        property_name='rate_divisor',
        count=10,
        column_type=Numeric,
        column_args=(21, 10),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    rateDivisors = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    payByBusinessPartner: Mapped[str] = mapped_column(
        'BPRPAY_0', Unicode(15, collation=DB_COLLATION), default=text("''")
    )
    payByBusinessPartnerAddress: Mapped[str] = mapped_column(
        'BPAPAY_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    companyName1: Mapped[str] = mapped_column('BPYNAM_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    companyName2: Mapped[str] = mapped_column('BPYNAM_1', Unicode(35, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPYADDLIG',
        property_name='address',
        count=3,
        column_type=Unicode,
        column_args=(50, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    addresses = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    payByBusinessPartnerPostalCode: Mapped[str] = mapped_column(
        'BPYPOSCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''")
    )
    payByBusinessPartnerCity: Mapped[str] = mapped_column(
        'BPYCTY_0', Unicode(40, collation=DB_COLLATION), default=text("''")
    )
    payByBusinessPartnerState: Mapped[str] = mapped_column(
        'BPYSAT_0', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    payByBusinessPartnerCountry: Mapped[str] = mapped_column(
        'BPYCRY_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    payByBusinessPartnerCountryName: Mapped[str] = mapped_column(
        'BPYCRYNAM_0', Unicode(40, collation=DB_COLLATION), default=text("''")
    )
    factor: Mapped[str] = mapped_column('BPRFCT_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    receipt: Mapped[str] = mapped_column('FCTVCR_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    validatedReceipt: Mapped[int] = mapped_column('FCTVCRFLG_0', SmallInteger, default=text('((0))'))
    receiptEntryNumber: Mapped[int] = mapped_column('QTCACCNUM_0', Integer, default=text('((0))'))
    dueDateCalculationStartDate: Mapped[datetime.datetime] = mapped_column(
        'STRDUDDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    paymentTerm: Mapped[str] = mapped_column('PTE_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    earlyDiscountOrLateCharge: Mapped[str] = mapped_column(
        'DEP_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    earlyDiscountOrLateChargeRate: Mapped[decimal.Decimal] = mapped_column(
        'DEPRAT_0', Numeric(8, 3), default=text('((0))')
    )
    taxRule: Mapped[str] = mapped_column('VAC_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    entityUserCode: Mapped[str] = mapped_column('SSTENTCOD_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    isDirectInvoice: Mapped[int] = mapped_column('DIRINVFLG_0', TINYINT, default=text('((0))'))
    intrastatProcessingNumber: Mapped[int] = mapped_column('EECNUMDEB_0', SmallInteger, default=text('((0))'))
    status: Mapped[int] = mapped_column('STA_0', TINYINT, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DES',
        property_name='comment',
        count=5,
        column_type=Unicode,
        column_args=(30, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    comments = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    originalInvoiceNumber: Mapped[str] = mapped_column(
        'INVNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    debitOrCredit: Mapped[int] = mapped_column('SNS_0', SmallInteger, default=text('((0))'))
    totalAmountIncludingTax: Mapped[decimal.Decimal] = mapped_column('AMTATI_0', Numeric(27, 13), default=text('((0))'))
    totalAmountExcludingTax: Mapped[decimal.Decimal] = mapped_column('AMTNOT_0', Numeric(27, 13), default=text('((0))'))
    totalAmountExcludingTaxInCompanyCurrency: Mapped[decimal.Decimal] = mapped_column(
        'AMTNOTL_0', Numeric(27, 13), default=text('((0))')
    )
    totalAmountIncludingTaxInCompanyCurrency: Mapped[decimal.Decimal] = mapped_column(
        'AMTATIL_0', Numeric(27, 13), default=text('((0))')
    )
    taxReferenceDate: Mapped[datetime.datetime] = mapped_column('VATDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    numberOfTaxes: Mapped[int] = mapped_column('NBRTAX_0', SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TAX',
        property_name='tax',
        count=10,
        column_type=Unicode,
        column_args=(5, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    taxes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BASTAX',
        property_name='taxBase',
        count=10,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    taxBasis = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='AMTTAX',
        property_name='amountTax',
        count=10,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    taxAmounts = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    theoreticalTaxAmount: Mapped[decimal.Decimal] = mapped_column('THEAMTTAX_0', Numeric(28, 8), default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='EXEAMTTAX',
        property_name='exemption_amount',
        count=10,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    exemptionAmount = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    billToCustomerAddress: Mapped[str] = mapped_column(
        'BPAINV_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    billToCustomerName1: Mapped[str] = mapped_column(
        'BPRNAM_0', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    billToCustomerName2: Mapped[str] = mapped_column(
        'BPRNAM_1', Unicode(35, collation=DB_COLLATION), default=text("''")
    )

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPAADDLIG',
        property_name='address_bpa',
        count=3,
        column_type=Unicode,
        column_args=(50, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    billToCustomerAddresses = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    billToCustomerPostalCode: Mapped[str] = mapped_column(
        'POSCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''")
    )
    billToCustomerCity: Mapped[str] = mapped_column('CTY_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    billToCustomerState: Mapped[str] = mapped_column('SAT_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    billToCustomerCountry: Mapped[str] = mapped_column('CRY_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    billToCustomerCountryName: Mapped[str] = mapped_column(
        'CRYNAM_0', Unicode(40, collation=DB_COLLATION), default=text("''")
    )
    draftNumber: Mapped[str] = mapped_column('BILVCR_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    stockMovementGroup: Mapped[str] = mapped_column('TRSFAM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    fiscalYear: Mapped[int] = mapped_column('FIY_0', SmallInteger, default=text('((0))'))
    period: Mapped[int] = mapped_column('PER_0', SmallInteger, default=text('((0))'))
    serviceStartDate: Mapped[datetime.datetime] = mapped_column(
        'STRDATSVC_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    serviceEndDate: Mapped[datetime.datetime] = mapped_column('ENDDATSVC_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    lastServiceAccountedDate: Mapped[datetime.datetime] = mapped_column(
        'LASDATSVC_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    usaSalesTaxAmount: Mapped[decimal.Decimal] = mapped_column('AMTTAXUSA_0', Numeric(28, 8), default=text('((0))'))
    caiNumber: Mapped[str] = mapped_column('CAI_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    caiValidityDate: Mapped[datetime.datetime] = mapped_column('DATVLYCAI_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    warehouse: Mapped[str] = mapped_column('WRHE_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    exportNumber: Mapped[int] = mapped_column('EXPNUM_0', Integer, default=text('((0))'))
    integralePartNumber: Mapped[str] = mapped_column('SINUM_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    isPrinted: Mapped[int] = mapped_column('STARPT_0', TINYINT, default=text('((1))'))
    isExternalDocument: Mapped[int] = mapped_column('ISEXTDOC_0', TINYINT, default=text('((0))'))
    earlyDiscountOrLateChargeBasis: Mapped[decimal.Decimal] = mapped_column(
        'BASDEP_0', Numeric(27, 13), default=text('((0))')
    )
    versionControlSystemNumber: Mapped[str] = mapped_column(
        'BELVCS_0', Unicode(12, collation=DB_COLLATION), default=text("''")
    )
    isValidatedAddress: Mapped[int] = mapped_column('ADRVAL_0', TINYINT, default=text('((0))'))
    priceOrAmountTaxType: Mapped[int] = mapped_column('SALPRITYP_0', TINYINT, default=text('((0))'))
    vatDeclarationNumber: Mapped[str] = mapped_column(
        'DCLEECNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    exportDeclaration: Mapped[str] = mapped_column(
        'POREXPDCL_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    mandate: Mapped[str] = mapped_column('UMRNUM_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    recurringNumber: Mapped[str] = mapped_column('RCRNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    recurringInvoicingDate: Mapped[datetime.datetime] = mapped_column(
        'RCRDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    numberOfCompanies: Mapped[int] = mapped_column('NBRCPY_0', SmallInteger, default=text('((1))'))
    cashVatTaxRule: Mapped[int] = mapped_column('CSHVAT_0', TINYINT, default=text('((0))'))
    derCode: Mapped[str] = mapped_column('SPADERNUM_0', Unicode(60, collation=DB_COLLATION), default=text("''"))
    field40Reason: Mapped[str] = mapped_column('FLD40REN_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    field41Reason: Mapped[str] = mapped_column('FLD41REN_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    originalDocumentNumber: Mapped[str] = mapped_column(
        'ORIDOCNUM_0', Unicode(30, collation=DB_COLLATION), default=text("''")
    )
    creditMemoReferenceStartDate: Mapped[datetime.datetime] = mapped_column(
        'PERDEB_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    creditMemoReferenceEndDate: Mapped[datetime.datetime] = mapped_column(
        'PERFIN_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    inPaymentSlipWithReferenceNumber: Mapped[str] = mapped_column(
        'BVRREFNUM_0', Unicode(27, collation=DB_COLLATION), default=text("''")
    )
    paymentBank: Mapped[str] = mapped_column('PAYBAN_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    cancellationStatus: Mapped[int] = mapped_column('REVCANSTA_0', SmallInteger, default=text('((0))'))
    project: Mapped[str] = mapped_column('PJTH_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    correctionMethod: Mapped[int] = mapped_column('METCOR_0', TINYINT, default=text('((0))'))
    siteIdentificationNumber: Mapped[str] = mapped_column(
        'CRN_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    spanishInvoiceType: Mapped[int] = mapped_column('INVTYPSPA_0', TINYINT, default=text('((0))'))
    businessProcessType: Mapped[str] = mapped_column(
        'BUSPROTYP_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    autoInvoicingSpanish: Mapped[int] = mapped_column('ISSBYREC_0', TINYINT, default=text('((0))'))
    manualAutoInvoicingSpaGenerated: Mapped[int] = mapped_column('ISSBYRECG_0', TINYINT, default=text('((0))'))
    automaticAutoInvoicingSpaGenerated: Mapped[int] = mapped_column('ISSAUTGEN_0', TINYINT, default=text('((0))'))

    # Específicos MOP
    recapitulative: Mapped[str] = mapped_column('XRECBPR_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    dua: Mapped[str] = mapped_column('XDUA_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    orderNumber: Mapped[str] = mapped_column('ZNUMENC_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    deliveryEndDate: Mapped[datetime.datetime] = mapped_column('XPDLVDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    quotationNumber: Mapped[str] = mapped_column('ZNUMPRO_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    paymentBank1: Mapped[str] = mapped_column('BAN_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    deliveryStartTime: Mapped[str] = mapped_column('XPETD_0', Unicode(6, collation=DB_COLLATION), default=text("''"))
    deliveryEndTime: Mapped[str] = mapped_column('XPETA_0', Unicode(6, collation=DB_COLLATION), default=text("''"))
    edition: Mapped[str] = mapped_column('ZEDICAO_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    editionPage: Mapped[str] = mapped_column('ZPAGINA_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    editionDate: Mapped[datetime.datetime] = mapped_column('ZDEDICAO_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    shippingStartDate: Mapped[datetime.datetime] = mapped_column(
        'XPSHIDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    licensePlate: Mapped[str] = mapped_column('XPLICPLATE_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    globalDocument: Mapped[str] = mapped_column('XPORDREF_0', Unicode(250, collation=DB_COLLATION), default=text("''"))
    globalDocumentDate: Mapped[datetime.datetime] = mapped_column(
        'XPORDDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    agency: Mapped[str] = mapped_column('ZAGENCIA_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    finalCustomer: Mapped[str] = mapped_column('ZCLIENTEF_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    reasonField40: Mapped[str] = mapped_column('XP_MOTF40_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    reasonField41: Mapped[str] = mapped_column('XP_MOTF41_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    accessCode: Mapped[str] = mapped_column('ZCODACES_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    startPeriod: Mapped[datetime.datetime] = mapped_column('XPPERDEB_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    endPeriod: Mapped[datetime.datetime] = mapped_column('XPPERFIN_0', DateTime, default=DEFAULT_LEGACY_DATETIME)

    details: Mapped[list['SalesInvoiceDetail']] = relationship(
        'SalesInvoiceDetail',
        primaryjoin='CustomerInvoiceHeader.invoiceNumber == foreign(SalesInvoiceDetail.invoiceNumber)',
        lazy='select',
        viewonly=True,
        uselist=False,
    )


class SalesInvoice(Base, AuditMixin, PrimaryKeyMixin, CreateUpdateDateMixin):
    __tablename__ = 'SINVOICEV'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='SINVOICEV_ROWID'),
        Index('SINVOICEV_SIV0', 'NUM_0', unique=True),
        Index('SINVOICEV_SIV1', 'SIHORI_0', 'SIHORINUM_0'),
        Index('SINVOICEV_SIV2', 'INVTYP_0', 'NUM_0', unique=True),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    invoiceNumber: Mapped[str] = mapped_column('NUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    salesSite: Mapped[str] = mapped_column('SALFCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    shippingSite: Mapped[str] = mapped_column('STOFCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    billToCustomer: Mapped[str] = mapped_column('BPCINV_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    soldToCustomer: Mapped[str] = mapped_column('BPCORD_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    groupCustomer: Mapped[str] = mapped_column('BPCGRU_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    shipToCustomerAddress: Mapped[str] = mapped_column(
        'BPAADD_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    customerInvoiceName1: Mapped[str] = mapped_column(
        'BPINAM_0', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    customerInvoiceName2: Mapped[str] = mapped_column(
        'BPINAM_1', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    billToCustomerEuropeanUnionVatNumber: Mapped[str] = mapped_column(
        'BPIEECNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    billToCustomerContact: Mapped[str] = mapped_column(
        'CNINAM_0', Unicode(15, collation=DB_COLLATION), default=text("''")
    )
    shipToCustomerName1: Mapped[str] = mapped_column(
        'BPDNAM_0', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    shipToCustomerName2: Mapped[str] = mapped_column(
        'BPDNAM_1', Unicode(35, collation=DB_COLLATION), default=text("''")
    )

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPDADDLIG',
        property_name='address_line',
        count=3,
        column_type=Unicode,
        column_args=(50, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    addressLine = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    shipToCustomerPostalCode: Mapped[str] = mapped_column(
        'BPDPOSCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''")
    )
    shipToCustomerCity: Mapped[str] = mapped_column('BPDCTY_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    shipToCustomerState: Mapped[str] = mapped_column(
        'BPDSAT_0', Unicode(35, collation=DB_COLLATION), default=text("''")
    )
    shipToCustomerCountry: Mapped[str] = mapped_column(
        'BPDCRY_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    shipToCustomerCountryName: Mapped[str] = mapped_column(
        'BPDCRYNAM_0', Unicode(40, collation=DB_COLLATION), default=text("''")
    )
    shipToCustomerContact: Mapped[str] = mapped_column(
        'CNDNAM_0', Unicode(15, collation=DB_COLLATION), default=text("''")
    )
    payByBusinessPartner: Mapped[str] = mapped_column(
        'BPRPAY_0', Unicode(15, collation=DB_COLLATION), default=text("''")
    )
    factor: Mapped[str] = mapped_column('BPRFCT_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    invoiceType: Mapped[str] = mapped_column('SIVTYP_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    category: Mapped[int] = mapped_column('INVTYP_0', TINYINT, default=text('((0))'))
    sourceDocumentCategory: Mapped[int] = mapped_column('SIHORI_0', TINYINT, default=text('((0))'))
    sourceDocumentNumber: Mapped[str] = mapped_column(
        'SIHORINUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    sourceDocumentDate: Mapped[datetime.datetime] = mapped_column(
        'SIHORIDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    invoiceDate: Mapped[datetime.datetime] = mapped_column('INVDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    currency: Mapped[str] = mapped_column('CUR_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    status: Mapped[int] = mapped_column('INVSTA_0', TINYINT, default=text('((1))'))
    isOnCreditMemo: Mapped[int] = mapped_column('INVCNOSTA_0', TINYINT, default=text('((0))'))
    hasStockTransaction: Mapped[int] = mapped_column('STOMVTFLG_0', TINYINT, default=text('((0))'))
    internalReference: Mapped[str] = mapped_column('INVREF_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    project: Mapped[str] = mapped_column('PJT_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    priceIncludingOrExcludingTax: Mapped[int] = mapped_column('PRITYP_0', TINYINT, default=text('((1))'))
    salesRep1: Mapped[str] = mapped_column('REP_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    salesRep2: Mapped[str] = mapped_column('REP_1', Unicode(15, collation=DB_COLLATION), default=text("''"))
    creditMemoReason: Mapped[str] = mapped_column('CNOREN_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    earlyDiscountOrLateCharge: Mapped[str] = mapped_column(
        'DEP_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    billToCustomerLanguage: Mapped[str] = mapped_column('LAN_0', Unicode(3, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TSCCOD',
        property_name='statistical',
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

    invoiceHeaderTextKey: Mapped[str] = mapped_column(
        'SIHTEX1_0', Unicode(17, collation=DB_COLLATION), default=text("''")
    )
    invoiceFooterTextKey: Mapped[str] = mapped_column(
        'SIHTEX2_0', Unicode(17, collation=DB_COLLATION), default=text("''")
    )
    isIntersite: Mapped[int] = mapped_column('BETFCY_0', TINYINT)
    isIntercompany: Mapped[int] = mapped_column('BETCPY_0', TINYINT)
    sourceSite: Mapped[str] = mapped_column('ORIFCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    purchaseInvoice: Mapped[str] = mapped_column('PIHNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DISCRGTYP',
        property_name='type',
        count=9,
        column_type=TINYINT,
        python_type=int,
        server_default=text('((0))'),
    )

    types = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTALIN',
        property_name='invoice_element_line',
        count=9,
        column_type=SmallInteger,
        python_type=int,
        server_default=text('((0))'),
    )

    invoiceElementLines = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    numberOfLines: Mapped[int] = mapped_column('LINNBR_0', SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTA',
        property_name='invoice_element',
        count=30,
        column_type=SmallInteger,
        python_type=int,
        server_default=text('((0))'),
    )

    invoiceElements = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTAAMT',
        property_name='percentage_amount',
        count=30,
        column_type=Numeric,
        column_args=(20, 5),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    percentageOrAmount = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTATYP',
        property_name='value_type',
        count=30,
        column_type=TINYINT,
        python_type=int,
        server_default=text('((0))'),
    )

    valueTypes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INVDTADSP',
        property_name='distribution_key',
        count=30,
        column_type=Unicode,
        column_args=(10, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    distributionKeys = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='SFISSTCOD',
        property_name='sage_tax_code',
        count=30,
        column_type=Unicode,
        column_args=(20, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    sageSalesTax = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PAM',
        property_name='payment_method',
        count=4,
        column_type=Unicode,
        column_args=(5, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    paymentMethodOfPrepayments = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INSATI',
        property_name='prepayment',
        count=4,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    prepaymentAmountIncludingTax = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INSORDNUM',
        property_name='sales_order',
        count=4,
        column_type=Unicode,
        column_args=(20, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    salesOrderOfPrepayment = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='INSLIN',
        property_name='sales_order_line',
        count=4,
        column_type=SmallInteger,
        python_type=int,
        server_default=text('((0))'),
    )

    salesOrderLineNumberOfPrepayment = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    numberOfInvoiceCopies: Mapped[int] = mapped_column('COPNBR_0', SmallInteger, default=text('((0))'))
    numberOfCreditMemoCopies: Mapped[int] = mapped_column('COPNBE_0', SmallInteger, default=text('((0))'))
    stockMovementCode: Mapped[str] = mapped_column('TRSCOD_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    stockAutomaticJournal: Mapped[str] = mapped_column(
        'ENTCOD_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    dockLocation: Mapped[str] = mapped_column('SRGLOCDEF_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    intrastatTransactionNature: Mapped[str] = mapped_column(
        'EECNAT_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    intrastatAdjustmentTransactionNature: Mapped[str] = mapped_column(
        'EECNATR_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    intrastatStatisticalRule: Mapped[str] = mapped_column(
        'EECSCH_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    intrastatAdjustmentStatisticalRule: Mapped[str] = mapped_column(
        'EECSCHR_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    intrastatTransportLocation: Mapped[int] = mapped_column('EECLOC_0', TINYINT, default=text('((0))'))
    intrastatTransportMode: Mapped[int] = mapped_column('EECTRN_0', TINYINT, default=text('((0))'))
    incoterm: Mapped[str] = mapped_column('EECICT_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    incotermTown: Mapped[str] = mapped_column('ICTCTY_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    forwardingAgent: Mapped[str] = mapped_column('FFWNUM_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    forwardingAgentAddress: Mapped[str] = mapped_column(
        'FFWADD_0', Unicode(5, collation=DB_COLLATION), default=text("''")
    )
    geographicCode: Mapped[str] = mapped_column('GEOCOD_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    insideCityLimits: Mapped[str] = mapped_column('INSCTYFLG_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    vertexTransactionType: Mapped[str] = mapped_column('VTT_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    exportNumber: Mapped[int] = mapped_column('EXPNUM_0', Integer, default=text('((0))'))
    marketingCampaign: Mapped[str] = mapped_column('CMGNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    marketingOperation: Mapped[str] = mapped_column('OPGNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    operationType: Mapped[str] = mapped_column('OPGTYP_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    priceStructure: Mapped[str] = mapped_column('PLISTC_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    totalQuantityDistributedOnLines: Mapped[decimal.Decimal] = mapped_column(
        'DSPTOTQTY_0', Numeric(22, 7), default=text('((0))')
    )
    totalWeightDistributedOnLines: Mapped[decimal.Decimal] = mapped_column(
        'DSPTOTWEI_0', Numeric(28, 13), default=text('((0))')
    )
    totalVolumeDistributedOnLines: Mapped[decimal.Decimal] = mapped_column(
        'DSPTOTVOL_0', Numeric(28, 13), default=text('((0))')
    )
    weightUnitForDistributionOnLines: Mapped[str] = mapped_column(
        'DSPWEU_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    volumeUnitForDistributionOnLines: Mapped[str] = mapped_column(
        'DSPVOU_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    isPrinted: Mapped[int] = mapped_column('STARPT_0', TINYINT, default=text('((1))'))
    isValidatedAddress: Mapped[int] = mapped_column('ADRVAL_0', TINYINT, default=text('((0))'))
    departureDate: Mapped[datetime.datetime] = mapped_column('DPEDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    arrivalDate: Mapped[datetime.datetime] = mapped_column('ARVDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    departureTime: Mapped[str] = mapped_column('ETD_0', Unicode(6, collation=DB_COLLATION), default=text("''"))
    arrivalTime: Mapped[str] = mapped_column('ETA_0', Unicode(6, collation=DB_COLLATION), default=text("''"))
    vehicleLicensePlate: Mapped[str] = mapped_column(
        'LICPLATE_0', Unicode(10, collation=DB_COLLATION), default=text("''")
    )
    trailerLicensePlate: Mapped[str] = mapped_column(
        'TRLLICPLATE_0', Unicode(10, collation=DB_COLLATION), default=text("''")
    )
    sourceDocumentType: Mapped[int] = mapped_column('SIHORITYP_0', TINYINT, default=text('((0))'))
    finalSequenceNumber: Mapped[str] = mapped_column(
        'SIHNUMEND_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    hasElectronicSignature: Mapped[int] = mapped_column('SIHCFMFLG_0', TINYINT, default=text('((0))'))

    # Específicos MOP
    campaignStartDate: Mapped[datetime.datetime] = mapped_column(
        'ZDATACAMP_0', DateTime, default=DEFAULT_LEGACY_DATETIME
    )
    customerReference: Mapped[str] = mapped_column('YVREF_0', Unicode(250, collation=DB_COLLATION), default=text("''"))

    # Específicos Saphety
    isSaphety: Mapped[int] = mapped_column('YSAPHFLG_0', TINYINT, default=text('((1))'))

    # Relacionamentos
    customer: Mapped['Customer'] = relationship(
        'Customer',
        primaryjoin='SalesInvoice.billToCustomer == foreign(Customer.customerCode)',
        lazy='joined',
        viewonly=True,
        uselist=False,
    )

    invoice_header: Mapped['CustomerInvoiceHeader'] = relationship(
        'CustomerInvoiceHeader',
        primaryjoin='SalesInvoice.invoiceNumber == foreign(CustomerInvoiceHeader.invoiceNumber)',
        lazy='joined',
        viewonly=True,
        uselist=False,
    )

    control: Mapped['SaphetyApiControl'] = relationship(
        'SaphetyApiControl',
        primaryjoin='SalesInvoice.invoiceNumber == foreign(SaphetyApiControl.invoiceNumber)',
        lazy='select',
        viewonly=True,
        uselist=False,
    )


class SalesInvoiceDetail(Base, AuditMixin, PrimaryKeyMixin, CreateUpdateDateMixin):
    __tablename__ = 'SINVOICED'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='SINVOICED_ROWID'),
        Index('SINVOICED_SID0', 'NUM_0', 'SIDLIN_0', unique=True),
        Index('SINVOICED_SID1', 'BPCINV_0', 'SALFCY_0', 'NUM_0', 'SIDLIN_0', unique=True),
        Index('SINVOICED_SID2', 'SOHNUM_0', 'CREDAT_0', 'NUM_0'),
        Index('SINVOICED_SID3', 'SDHNUM_0', 'SDDLIN_0'),
        Index('SINVOICED_SID4', 'CONNUM_0'),
        Index('SINVOICED_SID5', 'SRHNUM_0'),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    invoiceNumber: Mapped[str] = mapped_column('NUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    lineNumber: Mapped[int] = mapped_column('SIDLIN_0', Integer, default=text('((0))'))
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    salesOrderNumber: Mapped[str] = mapped_column('SOHNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    salesOrderLineNumber: Mapped[int] = mapped_column('SOPLIN_0', Integer, default=text('((0))'))
    salesOrderSequenceNumber: Mapped[int] = mapped_column('SOQSEQ_0', Integer, default=text('((0))'))
    salesDelivery: Mapped[str] = mapped_column('SDHNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    salesDeliveryLineNumber: Mapped[int] = mapped_column('SDDLIN_0', Integer, default=text('((0))'))
    serviceContractNumber: Mapped[str] = mapped_column(
        'CONNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    serviceRequest: Mapped[str] = mapped_column('SRENUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    stockTransferNumber: Mapped[str] = mapped_column(
        'SGHNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    sourceSalesInvoice: Mapped[str] = mapped_column(
        'SIHORINUM_0', Unicode(20, collation=DB_COLLATION), default=text("''")
    )
    sourceSalesInvoiceLine: Mapped[int] = mapped_column('SIDORILIN_0', Integer, default=text('((0))'))
    salesReturn: Mapped[str] = mapped_column('SRHNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    salesReturnLine: Mapped[int] = mapped_column('SRDLIN_0', Integer, default=text('((0))'))
    purchaseInvoiceLineNumber: Mapped[int] = mapped_column('PIDLIN_0', Integer, default=text('((0))'))
    billToCustomer: Mapped[str] = mapped_column('BPCINV_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    product: Mapped[str] = mapped_column('ITMREF_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    majorProductVersion: Mapped[str] = mapped_column(
        'ECCVALMAJ_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    minorProductVersion: Mapped[str] = mapped_column(
        'ECCVALMIN_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    productDescriptionUserLanguage: Mapped[str] = mapped_column(
        'ITMDES1_0', Unicode(30, collation=DB_COLLATION), default=text("''")
    )
    productDescriptionCustomerLanguage: Mapped[str] = mapped_column(
        'ITMDES_0', Unicode(30, collation=DB_COLLATION), default=text("''")
    )

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='VACITM',
        property_name='tax_level',
        count=3,
        column_type=Unicode,
        column_args=(5, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    taxLevels = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    sstTaxCode: Mapped[str] = mapped_column('SSTCOD_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    salesRep1: Mapped[str] = mapped_column('REP1_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    salesRep2: Mapped[str] = mapped_column('REP2_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    salesRep1CommissionRate: Mapped[decimal.Decimal] = mapped_column('REPRAT1_0', Numeric(8, 3), default=text('((0))'))
    salesRep2CommissionRate: Mapped[decimal.Decimal] = mapped_column('REPRAT2_0', Numeric(8, 3), default=text('((0))'))
    salesRep1CommissionBase: Mapped[decimal.Decimal] = mapped_column(
        'REPBAS1_0', Numeric(27, 13), default=text('((0))')
    )
    salesRep2CommissionBase: Mapped[decimal.Decimal] = mapped_column(
        'REPBAS2_0', Numeric(27, 13), default=text('((0))')
    )
    salesRep1CommissionAmount: Mapped[decimal.Decimal] = mapped_column(
        'REPAMT1_0', Numeric(27, 13), default=text('((0))')
    )
    salesRep2CommissionAmount: Mapped[decimal.Decimal] = mapped_column(
        'REPAMT2_0', Numeric(27, 13), default=text('((0))')
    )
    salesRepCommissionFactor: Mapped[decimal.Decimal] = mapped_column('REPCOE_0', Numeric(6, 3), default=text('((0))'))
    grossPrice: Mapped[decimal.Decimal] = mapped_column('GROPRI_0', Numeric(19, 5), default=text('((0))'))
    priceReason: Mapped[int] = mapped_column('PRIREN_0', SmallInteger, default=text('((0))'))
    netPrice: Mapped[decimal.Decimal] = mapped_column('NETPRI_0', Numeric(19, 5), default=text('((0))'))
    netPriceExcludingTax: Mapped[decimal.Decimal] = mapped_column('NETPRINOT_0', Numeric(19, 5), default=text('((0))'))
    netPriceIncludingTax: Mapped[decimal.Decimal] = mapped_column('NETPRIATI_0', Numeric(19, 5), default=text('((0))'))
    margin: Mapped[decimal.Decimal] = mapped_column('PFM_0', Numeric(27, 13), default=text('((0))'))
    costPrice: Mapped[decimal.Decimal] = mapped_column('CPRPRI_0', Numeric(19, 5), default=text('((0))'))
    discountOrCharge1: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL1_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge2: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL2_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge3: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL3_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge4: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL4_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge5: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL5_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge6: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL6_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge7: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL7_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge8: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL8_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge9: Mapped[list[decimal.Decimal]] = mapped_column(
        'DISCRGVAL9_0', Numeric(19, 5), default=text('((0))')
    )
    discountOrCharge1Reason: Mapped[int] = mapped_column('DISCRGREN1_0', SmallInteger, default=text('((0))'))
    discountOrCharge2Reason: Mapped[int] = mapped_column('DISCRGREN2_0', SmallInteger, default=text('((0))'))
    discountOrCharge3Reason: Mapped[int] = mapped_column('DISCRGREN3_0', SmallInteger, default=text('((0))'))
    discountOrCharge4Reason: Mapped[int] = mapped_column('DISCRGREN4_0', SmallInteger, default=text('((0))'))
    discountOrCharge5Reason: Mapped[int] = mapped_column('DISCRGREN5_0', SmallInteger, default=text('((0))'))
    discountOrCharge6Reason: Mapped[int] = mapped_column('DISCRGREN6_0', SmallInteger, default=text('((0))'))
    discountOrCharge7Reason: Mapped[int] = mapped_column('DISCRGREN7_0', SmallInteger, default=text('((0))'))
    discountOrCharge8Reason: Mapped[int] = mapped_column('DISCRGREN8_0', SmallInteger, default=text('((0))'))
    discountOrCharge9Reason: Mapped[int] = mapped_column('DISCRGREN9_0', SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='VAT',
        property_name='tax',
        count=3,
        column_type=Unicode,
        column_args=(5, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    taxes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    lineAmount: Mapped[decimal.Decimal] = mapped_column('AMTLIN_0', Numeric(27, 13), default=text('((0))'))
    lineAmountExcludingTax: Mapped[decimal.Decimal] = mapped_column(
        'AMTNOTLIN_0', Numeric(27, 13), default=text('((0))')
    )
    discountLineAmount: Mapped[decimal.Decimal] = mapped_column('AMTDEPLIN_0', Numeric(27, 13), default=text('((0))'))
    calculatedTaxableBase1: Mapped[decimal.Decimal] = mapped_column('CLCAMT1_0', Numeric(27, 13), default=text('((0))'))
    calculatedTaxableBase2: Mapped[decimal.Decimal] = mapped_column('CLCAMT2_0', Numeric(27, 13), default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BASTAXLIN',
        property_name='tax_basis',
        count=6,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    taxesBasisAmount = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    taxRates: Mapped[decimal.Decimal] = mapped_column('RATTAXLIN_0', Numeric(8, 3), default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='AMTTAXLIN',
        property_name='tax_amount',
        count=3,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    taxesAmount = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    lineAmountIncludingTax: Mapped[decimal.Decimal] = mapped_column(
        'AMTATILIN_0', Numeric(27, 13), default=text('((0))')
    )
    isLineWithDistributedInvoicingElement: Mapped[int] = mapped_column('DSPLINFLG_0', TINYINT, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DDTANUM',
        property_name='distr_invoice_number',
        count=9,
        column_type=SmallInteger,
        python_type=int,
        server_default=text('((0))'),
    )

    distributedLineInvoicingElementNumbers = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DDTANOT',
        property_name='distr_invoice_amount',
        count=9,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    distributedLineInvoicingElementAmounts = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DDTADEP',
        property_name='distr_invoice_discount',
        count=9,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    distributedLineInvoicingElementDiscounts = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    quantityInSalesUnit: Mapped[decimal.Decimal] = mapped_column('QTY_0', Numeric(28, 13), default=text('((0))'))
    quantityInStockUnit: Mapped[decimal.Decimal] = mapped_column('QTYSTU_0', Numeric(28, 13), default=text('((0))'))
    salesUnit: Mapped[str] = mapped_column('SAU_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    stockUnit: Mapped[str] = mapped_column('STU_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    salesUnitToStockUnitConversionFactor: Mapped[decimal.Decimal] = mapped_column(
        'SAUSTUCOE_0', Numeric(18, 7), default=text('((0))')
    )
    shippingSite: Mapped[str] = mapped_column('STOFCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    productStockManagement: Mapped[int] = mapped_column('STOMGTCOD_0', TINYINT, default=text('((0))'))
    exclusiveLotFilter: Mapped[str] = mapped_column('LOT_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    exclusiveStockStatusFilter: Mapped[str] = mapped_column(
        'STA_0', Unicode(12, collation=DB_COLLATION), default=text("''")
    )
    preferentialStockLocationFilter: Mapped[str] = mapped_column(
        'LOC_0', Unicode(10, collation=DB_COLLATION), default=text("''")
    )
    stockPriceInCreditMemoWithStockMovement: Mapped[decimal.Decimal] = mapped_column(
        'PRIORD_0', Numeric(27, 13), default=text('((0))')
    )
    allocationType: Mapped[int] = mapped_column('ALLTYP_0', TINYINT, default=text('((0))'))
    salesSite: Mapped[str] = mapped_column('SALFCY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    invoiceDate: Mapped[datetime.datetime] = mapped_column('INVDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TSICOD',
        property_name='statistical_group',
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

    lineType: Mapped[int] = mapped_column('LINTYP_0', TINYINT, default=text('((0))'))
    freeProduct: Mapped[int] = mapped_column('FOCFLG_0', TINYINT, default=text('((0))'))
    freeProductLineSource: Mapped[int] = mapped_column('ORILIN_0', Integer, default=text('((0))'))
    lineText: Mapped[str] = mapped_column('SIDTEX_0', Unicode(17, collation=DB_COLLATION), default=text("''"))
    isExtractedIntrastatLine: Mapped[int] = mapped_column('LINEECFLG_0', TINYINT, default=text('((0))'))
    isIntrastatPhysicalFlow: Mapped[int] = mapped_column('EECFLOPHY_0', TINYINT, default=text('((0))'))
    geographicCode: Mapped[str] = mapped_column('GEOCOD_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    insideCityLimits: Mapped[str] = mapped_column('INSCTYFLG_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    vertexTransactionSubtype: Mapped[str] = mapped_column(
        'VTS_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    vertexTransactionCode: Mapped[str] = mapped_column('VTC_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    isTaxedGeographically: Mapped[str] = mapped_column(
        'TAXGEOFLG_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    isTaxable: Mapped[int] = mapped_column('TAXFLG_0', SmallInteger, default=text('((0))'))
    isRecordedTax: Mapped[int] = mapped_column('TAXREGFLG_0', SmallInteger, default=text('((0))'))
    isPrintedOnInvoice: Mapped[int] = mapped_column('INVPRNBOM_0', TINYINT, default=text('((0))'))
    serviceStartDate: Mapped[datetime.datetime] = mapped_column('STRDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    serviceEndDate: Mapped[datetime.datetime] = mapped_column('ENDDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    servicePeriodNumber: Mapped[int] = mapped_column('PERNBR_0', SmallInteger, default=text('((0))'))
    servicePeriodType: Mapped[int] = mapped_column('PERTYP_0', TINYINT, default=text('((0))'))
    tokenManagement: Mapped[decimal.Decimal] = mapped_column('PITFLG_0', Numeric(28, 13), default=text('((0))'))
    weightDistributedOnLine: Mapped[decimal.Decimal] = mapped_column(
        'DSPLINWEI_0', Numeric(28, 13), default=text('((0))')
    )
    volumeDistributedOnLine: Mapped[decimal.Decimal] = mapped_column(
        'DSPLINVOL_0', Numeric(28, 13), default=text('((0))')
    )
    weightUnitForDistributionOnLines: Mapped[str] = mapped_column(
        'DSPWEU_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    volumeUnitForDistributionOnLines: Mapped[str] = mapped_column(
        'DSPVOU_0', Unicode(3, collation=DB_COLLATION), default=text("''")
    )
    warehouse: Mapped[str] = mapped_column('WRH_0', Unicode(1, collation=DB_COLLATION), default=text("''"))
    project: Mapped[str] = mapped_column('PJT_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    exportNumber: Mapped[int] = mapped_column('EXPNUM_0', Integer, default=text('((0))'))
    importLineNumber: Mapped[int] = mapped_column('IMPNUMLIG_0', Integer, default=text('((0))'))
    sourceDocumentType: Mapped[int] = mapped_column('SIDORI_0', TINYINT, default=text('((0))'))
    invoicePercentageForScheduledInvoice: Mapped[decimal.Decimal] = mapped_column(
        'INVPRC_0', Numeric(12, 5), default=text('((0))')
    )
    scheduledInvoiceLineNumber: Mapped[int] = mapped_column('VCRINVCNDLIN_0', Integer, default=text('((0))'))
    scheduledInvoiceSource: Mapped[int] = mapped_column('VCRINVCNDTYP_0', TINYINT, default=text('((0))'))
    projectSalesDocument: Mapped[str] = mapped_column(
        'SIDPSONUM_0', Unicode(1, collation=DB_COLLATION), default=text("''")
    )
    projectSalesDocumentLineNumber: Mapped[int] = mapped_column('SIDSEQNUM_0', SmallInteger, default=text('((0))'))
    reinvoicing: Mapped[int] = mapped_column('INVCNDUPD_0', TINYINT, default=text('((0))'))
    reinvoicingDate: Mapped[datetime.datetime] = mapped_column('NEXINVDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    scheduledInvoices: Mapped[str] = mapped_column('SVICNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))


class SalesInvoiceTax(Base, AuditMixin, PrimaryKeyMixin, CreateUpdateDateMixin):
    __tablename__ = 'SVCRVAT'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='SVCRVAT_ROWID'),
        Index('SVCRVAT_SVV0', 'VCRTYP_0', 'VCRNUM_0', 'VAT_0', unique=True),
        Index('SVCRVAT_SVV1', 'VCRTYP_0', 'VCRNUM_0', 'VATTYP_0', 'VAT_0', unique=True),
        Index('SVCRVAT_SVV2', 'NUM_0', 'VCRTYP_0', 'VCRNUM_0', 'VAT_0', unique=True),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    entryType: Mapped[int] = mapped_column('VCRTYP_0', TINYINT, default=text('((0))'))
    entryNumber: Mapped[str] = mapped_column('VCRNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    tax: Mapped[str] = mapped_column('VAT_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    taxType: Mapped[int] = mapped_column('VATTYP_0', TINYINT, default=text('((0))'))
    invoiceNumber: Mapped[str] = mapped_column('NUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    rate: Mapped[decimal.Decimal] = mapped_column('VATRAT_0', Numeric(16, 7), default=text('((0))'))
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    currency: Mapped[str] = mapped_column('CUR_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    taxBasis: Mapped[decimal.Decimal] = mapped_column('BASTAX_0', Numeric(27, 13), default=text('((0))'))
    taxAmount: Mapped[decimal.Decimal] = mapped_column('AMTTAX_0', Numeric(27, 13), default=text('((0))'))
    theoreticalTaxAmount: Mapped[decimal.Decimal] = mapped_column('THEAMTTAX_0', Numeric(28, 8), default=text('((0))'))
    exemptionAmount: Mapped[decimal.Decimal] = mapped_column('EXEAMTTAX_0', Numeric(27, 13), default=text('((0))'))
    grossBasis: Mapped[decimal.Decimal] = mapped_column('VATGRO_0', Numeric(27, 13), default=text('((0))'))
    subjectBasis: Mapped[decimal.Decimal] = mapped_column('VATNET_0', Numeric(27, 13), default=text('((0))'))
    taxAmount1: Mapped[decimal.Decimal] = mapped_column('VATAMT_0', Numeric(27, 13), default=text('((0))'))
    additionalTaxAmount: Mapped[decimal.Decimal] = mapped_column('VATSUPAMT_0', Numeric(27, 13), default=text('((0))'))
    discountBasisExcludingTax: Mapped[decimal.Decimal] = mapped_column(
        'BASDEPNOT_0', Numeric(27, 13), default=text('((0))')
    )
    discountBasisIncludingTax: Mapped[decimal.Decimal] = mapped_column(
        'BASDEPATI_0', Numeric(27, 13), default=text('((0))')
    )
    withHoldingTax: Mapped[int] = mapped_column('WITHOLTAXFLG_0', TINYINT, default=text('((0))'))
