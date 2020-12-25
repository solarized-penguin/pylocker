from assertpy.assertpy import AssertionBuilder


def is_successful_status_code(self: AssertionBuilder) -> AssertionBuilder:
    if 199 < self.val < 300:
        return self
    return self.error(f'Request failed! Status code: {self.val}')
