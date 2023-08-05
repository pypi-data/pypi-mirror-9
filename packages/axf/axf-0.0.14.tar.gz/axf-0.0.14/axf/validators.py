from PIL import Image
from tw2.core import validation
from tw2.core import Validator, ValidationError
from tw2.forms import FileValidator
import tg
from tg.i18n import lazy_ugettext as l_
import re

class PhoneNumberValidator(Validator):
    strip = True
    regex = re.compile(r'^\+[\d\s]+$')

    def _convert_to_python(self, value, state=None):
        value = super(PhoneNumberValidator, self)._convert_to_python(value)
        if value.startswith('00'):
            value = '+' + value[2:]
        return value

    def _validate_python(self, value, state=None):
        if not self.regex.match(value):
            raise ValidationError(l_('Not a valid internatinal phone number'), self)

class RangeDateValidator(Validator):
    def __init__(self, from_date, to_date, **kw):
        super(RangeDateValidator, self).__init__(**kw)
        self.from_date = from_date
        self.to_date = to_date

    def _validate_python(self, values, state=None):
        if values.get(self.from_date) > values.get(self.to_date):
            raise ValidationError(l_('Starting date must be previous than ending date'), self)


class ImageValidator(FileValidator):
    format = ()
    size = ()

    def __init__(self, **kw):
        super(ImageValidator, self).__init__(**kw)

    def _validate_python(self, image, state=None):
        try:
            img = Image.open(image.file)
            image.file.seek(0)
        except:
            raise ValidationError(l_('Invalid Image'), self)
        if self.format and img.format.lower() not in self.format:
            raise ValidationError(l_('Image format is invalid, must be %s' % (self.format,)), self)
        if self.size and img.size != self.size:
            raise ValidationError(l_('Image size must be %s * %s' % (self.size[0], self.size[1])), self)


class ConditionalTGValidator(Validator):
    def __init__(self, condition, validator):
        super(ConditionalTGValidator, self).__init__(required=False)
        self.condition = condition
        self.validator = validator

    def to_python(self, value, state):
        if self.condition(value):
            return self.validator.to_python(value, state)