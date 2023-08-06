from django.db import models
from datetime import datetime
from time import mktime
from django.utils.datastructures import DictWrapper


"""
To enable add to settings file:

PERMANENT_FIELD_CLASS = 'django_permanent.fields.NotNullTimestampField'
PERMANENT_FIELD_KWARGS = dict(
    default=False,
    blank=True,
    editable=False
)
"""


class NotNullTimestampField(models.DateTimeField):
    """ Field stores datetime as unix timestamp.
            None, False are stored as zero.
        Useful in case you need to provide unique together with removed field
    """
    null_repr = 0

    def __init__(self, *args, **kwargs):
        if kwargs.get('null', False):
            raise ValueError("This field is not nullable")
        if not 'default' in kwargs:
            raise ValueError("Default value is required")
        super(NotNullTimestampField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        try:
            return connection.creation.data_types['IntegerField'] % data
        except KeyError:
            return None

    def to_python(self, value):
        if not value:
            return self.default
        if isinstance(value, int):
            value = datetime.fromtimestamp(value)
        return super(NotNullTimestampField, self).to_python(value)

    def get_prep_value(self, value):
        if not value:
            return self.null_repr
        return int(mktime(value.timetuple()))

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value
