from enum import Enum


class UsernameStatus(str, Enum):
    ACTIVE = 'ACTIVE',
    """Username is active"""

    PENDING = 'PENDING',
    """Username is pending approval/moderation"""

    REJECTED = 'REJECTED'
    """Username was rejected during moderation"""


class TwoFactorDelivery(str, Enum):
    NONE = 'None',
    TextMessage = 'TextMessage'


class GrantType(str, Enum):
    Password = 'PASSWORD'
