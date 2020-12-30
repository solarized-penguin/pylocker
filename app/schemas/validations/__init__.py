class UserValidationRules:
    mobile_regex: str = r'^[0-9-]*$'
    password_regex: str = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$'

    full_name_error_message: str = 'You need to provide at least first and last name separated by spaces.'
    mobile_error_message: str = 'Mobile phone number can contain only numbers and dashes.'
    passwords_not_match_error_message: str = "Passwords don't match. " \
                                             "Password and password repeat must be identical."
    password_error_message: str = 'Password must contain at least: ' \
                                  '8 characters, 1 uppercase letter, ' \
                                  '1 lowercase letter and 1 number'
