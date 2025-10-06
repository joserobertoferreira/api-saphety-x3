import datetime
import decimal

from sqlalchemy import DateTime, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import DATABASE, DB_COLLATION, DEFAULT_LEGACY_DATETIME
from database.base import Base
from models.generics_mixins import ArrayColumnMixin
from models.mixins import AuditMixin, CreateUpdateDateMixin, DimensionMixin, DimensionTypesMixin, PrimaryKeyMixin


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
        property_name='taxBasie',
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

    taxAmount = _properties

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

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='AMTTAXUSA',
        property_name='tax_usa',
        count=10,
        column_type=Numeric,
        column_args=(27, 13),
        python_type=decimal.Decimal,
        server_default=text("''"),
    )

    usaSalesTaxAmount = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

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
    isCiusPT: Mapped[int] = mapped_column('YCIUSFLG_0', TINYINT, default=text('((1))'))


class SalesInvoice(Base, AuditMixin, PrimaryKeyMixin, CreateUpdateDateMixin, DimensionTypesMixin, DimensionMixin):
    __tablename__ = 'SINVOICEV'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='SINVOICEV_ROWID'),
        Index('SINVOICEV_SIV0', 'NUM_0', unique=True),
        Index('SINVOICEV_SIV1', 'SIHORI_0', 'SIHORINUM_0'),
        Index('SINVOICEV_SIV2', 'INVTYP_0', 'NUM_0', unique=True),
        {'schema': 'dbo'},
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
    isCiusPT: Mapped[int] = mapped_column('YCIUSFLG_0', TINYINT, default=text('((1))'))
