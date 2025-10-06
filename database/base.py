from config.settings import DATABASE
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

db_schema = str(DATABASE['SCHEMA'])

metadata_obj = MetaData(schema=db_schema)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    This class uses a custom metadata object to set the schema for all models.
    """

    metadata = metadata_obj
