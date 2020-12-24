import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, OID

db_schema = sa.MetaData()
"""Stores full schema information"""

files_table: sa.Table = sa.Table(
    'files', db_schema,
    sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
    sa.Column('oid', OID, nullable=False),
    sa.Column('owner_id', TEXT, nullable=True),
    sa.Column('file_path', TEXT, nullable=True, unique=True),
    sa.Column('file_size_bytes', INTEGER, nullable=True)
)
