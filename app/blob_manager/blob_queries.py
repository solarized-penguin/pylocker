create_empty_blob = "SELECT lo_creat(-1)"

write_data_to_blob = "SELECT lo_put(CAST(:loid AS OID), :offset, :data)"

read_data_from_blob = "SELECT lo_get(CAST(:loid AS OID), :offset, :length)"

delete_blob = "SELECT lo_unlink(CAST(:loid AS OID))"

get_size_of_blob = "SELECT get_lo_size(:loid)"
