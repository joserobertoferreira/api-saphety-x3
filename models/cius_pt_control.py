import datetime

from sqlalchemy import DateTime, Index, PrimaryKeyConstraint, Unicode, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import DATABASE, DB_COLLATION, DEFAULT_LEGACY_DATETIME
from database.base import Base
from models.mixins import AuditMixin, CreateUpdateDateMixin, PrimaryKeyMixin


class CiusPTControl(Base, AuditMixin, PrimaryKeyMixin, CreateUpdateDateMixin):
    __tablename__ = 'YCIUSCTL'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='YCIUSCTL_ROWID'),
        Index('YCIUSCTL_YCTL0', 'INVNUM_0', unique=True),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    invoiceNumber: Mapped[str] = mapped_column('INVNUM_0', Unicode(20, collation=DB_COLLATION), default=text("''"))
    sendDate: Mapped[datetime.datetime] = mapped_column('SNDDAT_0', DateTime, default=DEFAULT_LEGACY_DATETIME)
    message: Mapped[str] = mapped_column('MSGAPI_0', Unicode(255, collation=DB_COLLATION), default=text("''"))
    status: Mapped[int] = mapped_column('STAAPI_0', TINYINT, default=text('((1))'))
