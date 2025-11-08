from sqlalchemy import Index, Integer, PrimaryKeyConstraint, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from core.config.settings import DATABASE, DB_COLLATION
from core.database.base import Base

from .generics_mixins import ArrayColumnMixin
from .mixins import AuditMixin, CreateUpdateDateMixin, PrimaryKeyMixin


class Address(Base, AuditMixin, PrimaryKeyMixin, ArrayColumnMixin, CreateUpdateDateMixin):
    __tablename__ = 'BPADDRESS'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='BPADDRESS_ROWID'),
        Index('BPADDRESS_BPA0', 'BPATYP_0', 'BPANUM_0', 'BPAADD_0', unique=True),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    entityType: Mapped[int] = mapped_column('BPATYP_0', TINYINT, default=text('((0))'))
    entityNumber: Mapped[str] = mapped_column('BPANUM_0', Unicode(15, collation=DB_COLLATION), default=text("''"))
    code: Mapped[str] = mapped_column('BPAADD_0', Unicode(5, collation=DB_COLLATION), default=text("''"))
    description: Mapped[str] = mapped_column('BPADES_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    description1: Mapped[str] = mapped_column('ZBPAADD_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    defaultBankId: Mapped[str] = mapped_column('BPABID_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    isDefault: Mapped[int] = mapped_column('BPAADDFLG_0', TINYINT, default=text('((1))'))
    addressLine1: Mapped[str] = mapped_column('BPAADDLIG_0', Unicode(50, collation=DB_COLLATION), default=text("''"))
    addressLine2: Mapped[str] = mapped_column('BPAADDLIG_1', Unicode(50, collation=DB_COLLATION), default=text("''"))
    addressLine3: Mapped[str] = mapped_column('BPAADDLIG_2', Unicode(50, collation=DB_COLLATION), default=text("''"))
    postalCode: Mapped[str] = mapped_column('POSCOD_0', Unicode(10, collation=DB_COLLATION), default=text("''"))
    city: Mapped[str] = mapped_column('CTY_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    state: Mapped[str] = mapped_column('SAT_0', Unicode(35, collation=DB_COLLATION), default=text("''"))
    country: Mapped[str] = mapped_column('CRY_0', Unicode(3, collation=DB_COLLATION), default=text("''"))
    countryName: Mapped[str] = mapped_column('CRYNAM_0', Unicode(40, collation=DB_COLLATION), default=text("''"))
    nationalIDCode: Mapped[str] = mapped_column('CODSEE_0', Unicode(1, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TEL',
        property_name='phone',
        count=5,
        column_type=Unicode,
        column_args=(20, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    phones = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    faxNumber: Mapped[str] = mapped_column('FAX_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    mobile: Mapped[str] = mapped_column('MOB_0', Unicode(20, collation=DB_COLLATION), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='WEB',
        property_name='email',
        count=5,
        column_type=Unicode,
        column_args=(20, DB_COLLATION),
        python_type=str,
        server_default=text("''"),
    )

    emails = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    website: Mapped[str] = mapped_column('FCYWEB_0', Unicode(250, collation=DB_COLLATION), default=text("''"))
    externalIdentifier: Mapped[str] = mapped_column('EXTNUM_0', Unicode(30, collation=DB_COLLATION), default=text("''"))
    exportNumber: Mapped[int] = mapped_column('EXPNUM_0', Integer, default=text('((0))'))
    isValid: Mapped[int] = mapped_column('ADRVAL_0', TINYINT, default=text('((0))'))
    glnCode: Mapped[str] = mapped_column('GLNCOD_0', Unicode(13, collation=DB_COLLATION), default=text("''"))
    crn: Mapped[str] = mapped_column('CRN_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
