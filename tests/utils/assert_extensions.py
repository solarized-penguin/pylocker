from assertpy.assertpy import AssertionBuilder


def is_successful_status_code(self: AssertionBuilder) -> AssertionBuilder:
    if 199 < self.val < 300:
        return self
    return self.error(f'Request failed! Status code: {self.val}')


def is_validation_message_correct(
        self: AssertionBuilder, expected_message: str
) -> AssertionBuilder:
    message: str = self.val[0]['msg']
    if not expected_message == message:
        return self.error(f"Error messages don't match! "
                          f"Expected: {expected_message} "
                          f"Got: {message}")
    return self
