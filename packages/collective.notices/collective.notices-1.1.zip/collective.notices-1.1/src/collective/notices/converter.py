from collective.z3cform.datetimewidget.converter import DatetimeDataConverter \
    as BaseConverter

from dateutil.tz import gettz


class DatetimeDataConverter(BaseConverter):

    def toFieldValue(self, value):
        value = super(DatetimeDataConverter, self).toFieldValue(value)
        if value is not self.field.missing_value:
            if not getattr(value, 'tzinfo', None):
                value = value.replace(tzinfo=gettz())
        return value
