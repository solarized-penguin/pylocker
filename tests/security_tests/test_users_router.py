from datetime import datetime, date

from fastapi.testclient import TestClient

from app.security.enum_models import UsernameStatus

test_user_sign_up = {
    'email': 'test@domain.com',
    'fullName': 'FirstName LastName',
    'mobilePhone': '123-456-789',
    'password1': 'QwertY123',
    'password2': 'QwertY123',
    'imageUrl': 'https://www.image-host.com/avatar.png',
    'birthDate': date(2000, 1, 1),
}

test_user_info = {
    'email': 'test@domain.com',
    'fullName': 'FirstName LastName',
    'mobilePhone': '123-456-789',
    'id': 'test-user-id',
    'imageUrl': 'https://www.image-host.com/avatar.png',
    'birthDate': date(2000, 1, 1),
    'active': True,
    'passwordLastUpdateInstant': datetime.now(),
    'usernameStatus': UsernameStatus.ACTIVE,
    'twoFactorDelivery': None,
    'verified': True,
    'tenantId': 'test-tenant-id',
    'passwordChangeRequired': False,
    'insertInstant': datetime.now().timestamp(),
}


class TestSignUp:

    def test__model_filled_correctly__registration_successful(
            self, client: TestClient
    ) -> None:
        pass
