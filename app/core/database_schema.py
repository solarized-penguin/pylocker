import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, OID

db_schema = sa.MetaData()
"""Stores full schema information"""

files_table: sa.Table = sa.Table(
    'files', db_schema,
    sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
    sa.Column('oid', OID, nullable=False),
    sa.Column('owner_id', TEXT, nullable=False),
    sa.Column('file_path', TEXT, nullable=False),
    sa.Column('file_size_bytes', INTEGER, nullable=False),
    sa.Column('file_checksum', TEXT, nullable=False),
    UniqueConstraint('owner_id', 'file_path', name='unique_paths_per_user')
)
