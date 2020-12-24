create_empty_blob = "SELECT lo_creat(-1)"

write_data_to_blob = "SELECT lo_put(CAST(:loid AS OID), :offset, :data)"

read_data_from_blob = "SELECT lo_get(CAST(:loid AS OID), :offset, :length)"

delete_blob = "SELECT lo_unlink(CAST(:loid AS OID))"

get_size_of_blob = """
CREATE OR REPLACE FUNCTION pg_temp.get_lo_size(loid INTEGER)
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
SELECT pg_temp.get_lo_size(:loid);
"""
