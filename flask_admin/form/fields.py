import time
import datetime

from wtforms import fields, widgets
from flask.ext.admin.babel import gettext
from flask.ext.admin._compat import text_type, as_unicode

from . import widgets as admin_widgets

__all__ = ['DateTimeField', 'TimeField', 'Select2Field', 'Select2TagsField']

class DateTimeField(fields.DateTimeField):
    """
       Allows modifying the datetime format of a DateTimeField using form_args.
    """
    widget = admin_widgets.DateTimePickerWidget()
    def __init__(self, label=None, validators=None, format=None,
                 widget_format=None, **kwargs):
        """
            Constructor

            :param label:
                Label
            :param validators:
                Field validators
	        :param format:
                Format for text to date conversion. Defaults to '%Y-%m-%d %H:%M:%S'
            :param widget_format:
                Widget date format. Defaults to 'yyyy-mm-dd hh:ii:ss'
            :param kwargs:
                Any additional parameters
        """
        super(DateTimeField, self).__init__(label, validators, **kwargs)
		
        self.format = format or '%Y-%m-%d %H:%M:%S'
								   
        self.widget_format = widget_format or 'yyyy-mm-dd hh:ii:ss'
        
class TimeField(fields.Field):
    """
        A text field which stores a `datetime.time` object.
        Accepts time string in multiple formats: 20:10, 20:10:00, 10:00 am, 9:30pm, etc.
    """
    widget = admin_widgets.TimePickerWidget()

    def __init__(self, label=None, validators=None, formats=None,
                 default_format=None, widget_format=None, **kwargs):
        """
            Constructor

            :param label:
                Label
            :param validators:
                Field validators
            :param formats:
                Supported time formats, as a enumerable.
            :param default_format:
                Default time format. Defaults to '%H:%M:%S'
            :param widget_format:
                Widget date format. Defaults to 'hh:ii:ss'
            :param kwargs:
                Any additional parameters
        """
        super(TimeField, self).__init__(label, validators, **kwargs)

        self.formats = formats or ('%H:%M:%S', '%H:%M',
                                   '%I:%M:%S%p', '%I:%M%p',
                                   '%I:%M:%S %p', '%I:%M %p')

        self.default_format = default_format or '%H:%M:%S'
        self.widget_format = widget_format or 'hh:ii:ss'

    def _value(self):
        if self.raw_data:
            return u' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.default_format) or u''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = u' '.join(valuelist)

            for format in self.formats:
                try:
                    timetuple = time.strptime(date_str, format)
                    self.data = datetime.time(timetuple.tm_hour,
                                              timetuple.tm_min,
                                              timetuple.tm_sec)
                    return
                except ValueError:
                    pass

            raise ValueError(gettext('Invalid time format'))


class Select2Field(fields.SelectField):
    """
        `Select2 <https://github.com/ivaynberg/select2>`_ styled select widget.

        You must include select2.js, form.js and select2 stylesheet for it to
        work.
    """
    widget = admin_widgets.Select2Widget()

    def __init__(self, label=None, validators=None, coerce=text_type,
                 choices=None, allow_blank=False, blank_text=None, **kwargs):
        super(Select2Field, self).__init__(
            label, validators, coerce, choices, **kwargs
        )
        self.allow_blank = allow_blank
        self.blank_text = blank_text or ' '

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)

        for value, label in self.choices:
            yield (value, label, self.coerce(value) == self.data)

    def process_data(self, value):
        if value is None:
            self.data = None
        else:
            try:
                self.data = self.coerce(value)
            except (ValueError, TypeError):
                self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                try:
                    self.data = self.coerce(valuelist[0])
                except ValueError:
                    raise ValueError(self.gettext(u'Invalid Choice: could not coerce'))

    def pre_validate(self, form):
        if self.allow_blank and self.data is None:
            return

        super(Select2Field, self).pre_validate(form)


class Select2TagsField(fields.TextField):
    """`Select2 <http://ivaynberg.github.com/select2/#tags>`_ styled text field.
    You must include select2.js, form.js and select2 stylesheet for it to work.
    """
    widget = admin_widgets.Select2TagsWidget()

    def __init__(self, label=None, validators=None, save_as_list=False, coerce=text_type, **kwargs):
        """Initialization

        :param save_as_list:
            If `True` then populate ``obj`` using list else string
        """
        self.save_as_list = save_as_list
        self.coerce = coerce

        super(Select2TagsField, self).__init__(label, validators, **kwargs)

    def process_formdata(self, valuelist):
        if self.save_as_list:
            self.data = [self.coerce(v.strip()) for v in valuelist[0].split(',') if v.strip()]
        else:
            self.data = self.coerce(valuelist[0])

    def _value(self):
        if isinstance(self.data, (list, tuple)):
            return u','.join(as_unicode(v) for v in self.data)
        elif self.data:
            return as_unicode(self.data)
        else:
            return u''
