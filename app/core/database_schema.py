import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
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

get_blob_size = PGFunction(
    schema='public',
    signature='get_lo_size(loid INTEGER)',
    definition="""
    RETURNS BIGINT AS $lo_size$
    DECLARE
        file_descriptor INTEGER;
        file_size BIGINT;
    BEGIN
        -- Open large object for reading.
        -- Parameter "x'40000'" is equivalent to postgres large object mode "INV_READ"
        -- which is necessary for method to work
        file_descriptor := lo_open(CAST(loid AS OID), x'40000' :: INT);
    
        -- Seek to the end
        -- "Seek" command = "2"
        PERFORM lo_lseek64(file_descriptor, 0, 2);
    
        -- Fetch current file position - location of the last byte
        file_size := lo_tell64(file_descriptor);
    
        -- Close open file.
        PERFORM lo_close(file_descriptor);
    
        RETURN file_size;
    END;
    $lo_size$
    LANGUAGE plpgsql;
    """
)
