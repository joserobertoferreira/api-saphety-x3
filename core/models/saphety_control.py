import datetime

from sqlalchemy import Date, DateTime, Index, PrimaryKeyConstraint, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from core.config.settings import DATABASE, DB_COLLATION, DEFAULT_LEGACY_DATE
from core.database.base import Base

from .mixins import AuditMixin, PrimaryKeyMixin


class SaphetyApiControl(Base, AuditMixin, PrimaryKeyMixin):
    __tablename__ = 'YSAPHCTL'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='YSAPHCTL_ROWID'),
        Index('YSAPHCTL_YCTL0', 'INVNUM_0', unique=True),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    invoiceNumber: Mapped[str] = mapped_column('INVNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    sendDate: Mapped[datetime.date] = mapped_column('SNDDAT_0', Date, default=DEFAULT_LEGACY_DATE)
    filename: Mapped[str] = mapped_column('FICHIER_0', Unicode(255, collation=DB_COLLATION), default=text("''"))
    message: Mapped[str] = mapped_column('MSGAPI_0', Unicode(255, collation=DB_COLLATION), default=text("''"))
    status: Mapped[int] = mapped_column('STAAPI_0', TINYINT, default=text('((1))'))
    requestStatus: Mapped[int] = mapped_column('STAREQ_0', TINYINT, default=text('((1))'))
    integrationStatus: Mapped[int] = mapped_column('STAINT_0', TINYINT, default=text('((1))'))
    notificationStatus: Mapped[int] = mapped_column('STANOT_0', TINYINT, default=text('((1))'))
    requestId: Mapped[str] = mapped_column('REQUESTID_0', Unicode(50, collation=DB_COLLATION), default=text("''"))
    financialId: Mapped[str] = mapped_column('OUTFINID_0', Unicode(50, collation=DB_COLLATION), default=text("''"))


class APIControlView(Base):
    __tablename__ = 'YVWSAPHCTL'
    __table_args__ = (
        PrimaryKeyConstraint('INVNUM_0'),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    invoiceNumber: Mapped[str] = mapped_column('INVNUM_0', Unicode(20, collation=DB_COLLATION))
    category: Mapped[int] = mapped_column('INVTYP_0', TINYINT)
    invoiceDate: Mapped[datetime.date] = mapped_column('INVDAT_0', Date)
    filename: Mapped[str] = mapped_column('FICHIER_0', Unicode(255, collation=DB_COLLATION))
    sendDate: Mapped[datetime.date] = mapped_column('SNDDAT_0', Date)
    message: Mapped[str] = mapped_column('MSGAPI_0', Unicode(255, collation=DB_COLLATION))
    status: Mapped[int] = mapped_column('STAAPI_0', TINYINT)
    requestStatus: Mapped[int] = mapped_column('STAREQ_0', TINYINT)
    integrationStatus: Mapped[int] = mapped_column('STAINT_0', TINYINT)
    notificationStatus: Mapped[int] = mapped_column('STANOT_0', TINYINT)
    requestId: Mapped[str] = mapped_column('REQUESTID_0', Unicode(50, collation=DB_COLLATION))
    financialId: Mapped[str] = mapped_column('OUTFINID_0', Unicode(50, collation=DB_COLLATION))
    createDatetime: Mapped[datetime.datetime] = mapped_column('CREDATTIM_0', DateTime, nullable=False)
    updateDatetime: Mapped[datetime.datetime] = mapped_column('UPDDATTIM_0', DateTime, nullable=False)
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, collation=DB_COLLATION))
    sender: Mapped[str] = mapped_column('SENDER_0', Unicode(20, collation=DB_COLLATION))
    receiver: Mapped[str] = mapped_column('RECEIVER_0', Unicode(20, collation=DB_COLLATION))
    customer: Mapped[str] = mapped_column('BPCNUM_0', Unicode(15, collation=DB_COLLATION))
    saphetyType: Mapped[int] = mapped_column('SAPHTYP_0', TINYINT)
