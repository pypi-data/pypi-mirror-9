import zxcvbn

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


# Settings
PASSWORD_MIN_LENGTH = getattr(settings, "PASSWORD_MIN_LENGTH", 8)
PASSWORD_MAX_LENGTH = getattr(settings, "PASSWORD_MAX_LENGTH", 128)
PASSWORD_MIN_ENTROPY = getattr(settings, "ZXCVBN_MIN_ENTROPY", 25)
PASSWORD_MIN_LENGTH_MESSAGE = getattr(settings, "PASSWORD_MIN_LENGTH_MESSAGE", "Password must be %s characters or more.")
PASSWORD_MAX_LENGTH_MESSAGE = getattr(settings, "PASSWORD_MAX_LENGTH_MESSAGE", "Password must be %s characters or less.")
PASSWORD_MIN_ENTROPY_MESSAGE = getattr(settings, "PASSWORD_MIN_ENTROPY_MESSAGE", "Password must be more complex")

class LengthValidator(object):
    code = "length"

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(
                message=PASSWORD_MIN_LENGTH_MESSAGE % self.min_length,
                code=self.code)
        elif self.max_length and len(value) > self.max_length:
            raise ValidationError(
                message=PASSWORD_MAX_LENGTH_MESSAGE % self.max_length,
                code=self.code)


class ZXCVBNValidator(object):
    code = "zxcvbn"

    def __call__(self, value):
        res = zxcvbn.password_strength(value)
        if res.get('entropy') < PASSWORD_MIN_ENTROPY:
            raise ValidationError(PASSWORD_MIN_ENTROPY_MESSAGE, code=self.code)


length_validator = LengthValidator(PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH)
max_length_validator = LengthValidator(max_length=PASSWORD_MAX_LENGTH)
zxcvbn_validator = ZXCVBNValidator()
