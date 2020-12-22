from .auth_client import AuthClient


def create_auth_client() -> AuthClient:
    """
    Factory method returning AuthClient.
    """
    return AuthClient()
