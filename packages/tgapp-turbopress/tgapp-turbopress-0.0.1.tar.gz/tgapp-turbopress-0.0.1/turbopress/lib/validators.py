from datetime import datetime
from formencode.validators import FancyValidator, Invalid


class NaiveDateTimeValidator(FancyValidator):
    def _to_python(self, value, status):
        date_string = value.strip()
        try:
            date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M')
        except:
            raise Invalid('date must be in format yyyy-mm-ddThh:mm', value, status)
        return date

    _convert_to_python = _to_python