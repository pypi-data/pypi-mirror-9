# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import shutil
import tempfile
import datetime
import copy
import pytz
import re
from collections import deque
import logging

import dateutil
from django import forms
from django.forms.util import from_current_timezone, ErrorDict
from django.core.files.uploadedfile import UploadedFile
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.widgets import FileInput, TextInput
from django.forms import widgets
from steelscript.common.timeutils import \
    (parse_timedelta, timedelta_total_seconds, timedelta_str)

from steelscript.appfwk.apps.datasource.models import Criteria, TableField

logger = logging.getLogger(__name__)

DURATIONS = ('1 min', '15 min', '1 hour',
             '2 hours', '4 hours', '12 hours',
             '1 day', '1 week', '4 weeks')


class CriteriaError(Exception):
    """ Exception raised when a problem resolving criteria occurs. """
    pass


class CriteriaTemplateError(CriteriaError):
    pass


class CriteriaPostProcessError(CriteriaError):
    pass

# Map of all possible timezone names to tzinfo structures
ALL_TIMEZONES_MAP = None


def all_timezones_map():
    global ALL_TIMEZONES_MAP
    if ALL_TIMEZONES_MAP is None:
        ALL_TIMEZONES_MAP = dict((n, pytz.timezone(n))
                                 for n in pytz.all_timezones)
    return ALL_TIMEZONES_MAP


class DateWidget(forms.DateInput):
    """ Custom DateWidget """

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'date'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(DateWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs):
        initial_date = attrs.get('initial_date', None)
        if initial_date:
            m = re.match("now *- *(.+)", initial_date)
            if m:
                secs = timedelta_total_seconds(parse_timedelta(m.group(1)))
                initial_date = (
                    "d = new Date(); d.setSeconds(d.getSeconds()-%d);" \
                    % secs)
            else:
                initial_date = "d = '%s';" % initial_date
        else:
            initial_date = "d = new Date();"
        msg = '''
        {0} <span id="datenow_{name}" class="icon-calendar" title="Set date to today"> </span>
        <script type="text/javascript">
              $("#id_{name}").datepicker({{
                 format: "mm/dd/YY",
                 defaultDate: +2,
                 autoclose: true
              }});
              {initial_date}
              $("#id_{name}").datepicker("setDate", d);
              $("#datenow_{name}").click(function() {{ $("#id_{name}").datepicker("setDate", new Date()); }});
          </script>
          '''
        return msg.format(
            super(DateWidget, self).render(name, value, attrs),
            name=name, initial_date=initial_date
        )


class TimeWidget(forms.TimeInput):
    """ Custom TimeWidget for Reports
    """

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'time'}
        if attrs is not None:
            final_attrs.update(attrs)

        super(TimeWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs):
        initial_time = attrs.get('initial_time', None)
        if initial_time:
            m = re.match("now *- *(.+)", initial_time)
            if m:
                secs = timedelta_total_seconds(parse_timedelta(m.group(1)))
                initial_time = (
                    "d = new Date(); d.setSeconds(d.getSeconds()-%d);" \
                    % secs)
            else:
                initial_time = "d = '%s';" % initial_time
        else:
            initial_time = "d = new Date();"
        msg = '''
        {0} <span id="timenow_{name}" class="icon-time" title="Set time/date to now"> </span>
        <script type="text/javascript">
              $("#id_{name}").timepicker({{
                 step: 15,
                 scrollDefaultNow:true,
                 timeFormat:"g:i:s a"
              }});
              $("#timenow_{name}").click(function() {{
                 $("#id_{name}").timepicker("setTime", new Date());
              }});
              {initial_time}
              $("#id_{name}").timepicker("setTime", d);
        </script>
        '''
        #'$("#id_{name}").timepicker("setTime", new Date());'
        return msg.format(
            super(TimeWidget, self).render(name, value, attrs),
            name=name, initial_time=initial_time
        )


class ReportSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """ A SplitDateTime Widget that uses overridden Report widgets
    """
    def __init__(self, attrs=None):
        split_widgets = [DateWidget, TimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, split_widgets, attrs)


class ReportSplitDateWidget(forms.SplitDateTimeWidget):
    """A Date Widget with """
    def __init__(self, attrs=None):
        # Simply using DateWidget will not work, the javascript code
        # will be displayed on browser instead of rendering the widget
        # Using MultiWidget can render the widget correctly
        forms.MultiWidget.__init__(self, [DateWidget], attrs)


class FileSelectField(forms.Field):
    def to_python(self, data):
        if data in validators.EMPTY_VALUES:
            return None

        if isinstance(self.widget, TextInput):
            return data

        elif isinstance(self.widget, FileInput):

            # UploadedFile objects should have name and size attributes.
            try:
                file_name = data.name
                file_size = data.size
            except AttributeError:
                raise ValidationError(self.error_messages['invalid'])

            if not file_name:
                raise ValidationError(self.error_messages['invalid'])

            # look for uploaded files, save them off to another
            # temporary file and return the path for use in JSON
            # consumers of this file will need to clean them up
            # TODO this will be replaced by the File Storage App
            newtemp = tempfile.NamedTemporaryFile(delete=False)
            data.seek(0)
            shutil.copyfileobj(data, newtemp)
            data.close()
            newtemp.close()
            return newtemp.name
        else:
            raise ValidationError('Unsupported widget source: %s' %
                                  str(self.widget))


class DateTimeField(forms.DateTimeField):
    """Field that takes a date/time string and parses it to datetime object.
    """

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None

        if isinstance(value, list):
            # This came from SplitDateTimeWidget so the value is two strings
            value = ' '.join(value)

        if isinstance(value, str) or isinstance(value, unicode):
            try:
                v = dateutil.parser.parse(value, tzinfos=all_timezones_map())
            except:
                raise ValidationError('Invalid date/time string: %s' % value)

            return from_current_timezone(v)

        if isinstance(value, datetime.datetime):
            return from_current_timezone(value)

        if isinstance(value, datetime.date):
            result = datetime.datetime(value.year, value.month, value.day)
            return from_current_timezone(result)

        raise ValidationError('Unknown data/time field value type: %s' %
                              type(value))


class DurationWidget(forms.MultiWidget):

    def __init__(self,
                 choices=((60, '1 minute'),
                          (60*15, '15 minutes'),
                          (60*60, 'Hour'),
                          (60*60*6, '6 Hour')),
                 **kwargs):
        self.choices = choices
        split_widgets = [widgets.Select(choices=choices),
                         widgets.TextInput()]
        super(DurationWidget, self).__init__(split_widgets)

    def decompress(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            value = timedelta_total_seconds(parse_timedelta(value))

        if value:
            m = [v for v in self.choices if v[0] == value]
            if len(m) == 1:
                return m[0]
            else:
                return [0, '%d min' % (value / 60)]

        return [None, None]


class DurationField(forms.ChoiceField):
    """ Field that takes duration string and parses it to timedelta object. """

    def __init__(self, **kwargs):
        self._special_values = kwargs.pop('special_values', None)
        initial = kwargs.pop('initial', None)
        if ((initial is not None) and
              (self._special_values is None or
               initial not in self._special_values)):
            initial_td = parse_timedelta(initial)
            initial_valid = False
        else:
            initial_td = None
            initial_valid = True
        choices = []

        # Rebuild the choices list to ensure that
        # the value is normalized using timedelta_str
        for choice in kwargs.pop('choices'):
            td = None
            if not (isinstance(choice, list) or isinstance(choice, tuple)):
                if (self._special_values is None or
                        choice not in self._special_values):
                    td = parse_timedelta(choice)
                    td_str = timedelta_str(td)
                    value = td_str
                    label = td_str
                else:
                    value = choice
                    label = choice

            else:
                (value, label) = choice
                if (self._special_values is None or
                        value not in self._special_values):
                    td = parse_timedelta(value)
                    value = timedelta_str(td)

            choice = (value, label)
            choices.append(choice)

            if initial_td is not None and initial_td == td:
                initial = value
                initial_valid = True

        kwargs['choices'] = choices
        if not initial_valid:
            raise KeyError('Initial duration is invalid: %s' % initial)

        super(DurationField, self).__init__(initial=initial, **kwargs)

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            v = None
        elif self._special_values and value in self._special_values:
            v = value
        else:
            try:
                v = parse_timedelta(value)
            except:
                raise ValidationError('Invalid duration string: %s' % value)

        return v

    def validate(self, value):
        pass


def fields_add_time_selection(obj, show_duration=True, initial_duration=None,
                              durations=None, show_start=False,
                              initial_start_time='now-1h',
                              initial_start_date='now-1h', show_end=True,
                              initial_end_time='now-0',
                              initial_end_date='now-0',
                              special_values=None):

    if show_start:
        field = TableField(keyword='starttime',
                           label='Start Time',
                           field_cls=DateTimeField,
                           field_kwargs={
                               'widget': ReportSplitDateTimeWidget,
                               'widget_attrs': {
                                   'initial_time': initial_start_time,
                                   'initial_date': initial_start_date
                               }
                           },
                           required=False)
        field.save()
        obj.fields.add(field)

    if show_end:
        field = TableField(keyword='endtime',
                           label='End Time',
                           field_cls=DateTimeField,
                           field_kwargs={
                               'widget': ReportSplitDateTimeWidget,
                               'widget_attrs': {
                                   'initial_time': initial_end_time,
                                   'initial_date': initial_end_date
                               }
                           },
                           required=False)
        field.save()
        obj.fields.add(field)

    if show_duration:
        if durations is None:
            durations = DURATIONS

        field = TableField(keyword='duration',
                           label='Duration',
                           initial=initial_duration,
                           field_cls=DurationField,
                           field_kwargs={'choices': durations,
                                         'special_values': special_values},
                           required=False)
        field.save()
        obj.fields.add(field)


def fields_add_resolution(obj, initial=None,
                          resolutions=None,
                          special_values=None):

    if resolutions is None:
        resolutions = ('1m', '15m', '1h', '6h')

    field = TableField(keyword='resolution',
                       label='Data Resolution',
                       field_cls=DurationField,
                       field_kwargs={'choices': resolutions,
                                     'special_values': special_values},
                       initial=initial)
    field.save()
    obj.fields.add(field)


class TableFieldForm(forms.Form):
    """ Form built from a set of TableFields.
    """
    # css definitions
    error_css_class = 'text-error'

    # special hidden field definitions
    ignore_cache = forms.BooleanField(required=False, widget=forms.HiddenInput)
    debug = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, tablefields, use_widgets=True, hidden_fields=None,
                 include_hidden=False, **kwargs):
        """ Initialize a TableFieldForm for the given set of table.

        :param tablefields: dict of id to TableField

        :param use_widgets: if True (default) include UI-style widgets,
            otherwise (False) use only TextInput (suitable for command-line)

        Standard Form arguments `data` and `files` should be used
        as kwargs instead of passing as positional args.

        """

        if 'data' in kwargs and kwargs['data'] is not None:
            # Make a copy of data as we may change it below
            kwargs['data'] = copy.copy(kwargs['data'])

        super(TableFieldForm, self).__init__(**kwargs)

        self._tablefields = tablefields
        self._use_widgets = use_widgets
        self._hidden_fields = hidden_fields

        for id_ in self.compute_field_precedence():
            tablefield = self._tablefields[id_]
            if include_hidden or not (tablefield.hidden or
                                      (hidden_fields and
                                       tablefield.keyword in hidden_fields)):
                self.add_field(id_, tablefield)

    def add_field_error(self, field_id, msg):
        if self._errors is None:
            self._errors = ErrorDict()
        self._errors[field_id] = self.error_class([msg])

    def add_field(self, field_id, tablefield):
        if field_id in self.fields:
            # Already added this field
            return

        field_cls = tablefield.field_cls or forms.CharField

        if tablefield.field_kwargs is not None:
            fkwargs = copy.copy(tablefield.field_kwargs)
        else:
            fkwargs = {}

        if not self._use_widgets:
            fkwargs['widget'] = TextInput

        if 'widget_attrs' in fkwargs:
            widget_attrs = fkwargs.get('widget_attrs')
            del fkwargs['widget_attrs']
        else:
            widget_attrs = None

        for k in ['label', 'required', 'help_text', 'initial']:
            fkwargs[k] = getattr(tablefield, k)

        func = tablefield.pre_process_func
        if func is not None:
            try:
                func(self, field_id, fkwargs)
            except Exception as e:
                logger.exception('Pre processing failed: %s' % field_id)
                msg = ("Pre-process function '%s' returned an exception: %s" %
                       (str(func), str(e)))
                self.add_field_error(field_id, msg)

        field = field_cls(**fkwargs)
        self.fields[field_id] = field

        if self.data is not None and field_id not in self.data:

            # If using widgets, sometimes formboolean fields are
            # omitted from self.data if unchecked, thus we need to
            # *not* fill in the initial value.

            if (  (not self._use_widgets or
                   tablefield.field_cls != forms.BooleanField) and
                  (tablefield.initial is not None)):
                self.data[field_id] = tablefield.initial
            elif ('choices' in fkwargs) and len(fkwargs['choices']) > 0:
                self.data[field_id] = fkwargs['choices'][0][0]

        f = field_cls(**fkwargs)
        self.fields[field_id] = f
        f.widget.attrs.update({'onchange': 'rvbd.report.criteriaChanged()'})
        if widget_attrs:
            f.widget.attrs.update(widget_attrs)

    def compute_field_precedence(self):
        ids = self._tablefields.keys()

        # List of fields that are still unset after this iteration
        unprocessed_ids = deque(ids)
        ordered_ids = []

        last_not_ready_id = None

        # ids is the *complete* list of fields that must be processed
        while unprocessed_ids:
            id_ = unprocessed_ids.popleft()
            tablefield = self._tablefields[id_]

            ready = True
            if tablefield.parent_keywords is not None:
                # ids take two forms:
                #   - <keyword>
                #   - __s<sectionid>_<keyword>

                m = re.match('^(__s[0-9]_)(.*)$', id_)
                if m:
                    section = m.group(1)
                    keyword = m.group(2)
                else:
                    section = None
                    keyword = id_

                for parent_keyword in tablefield.parent_keywords:
                    # Now, parents are <keyword> only, they never reference
                    # a section.  If the field in question has a section
                    # look first to see if a keyword in the same section exists
                    # at all, and if it does whether it's processed

                    if section and (section + parent_keyword) in ids:
                        check_keyword = section+parent_keyword
                    else:
                        check_keyword = parent_keyword

                    if check_keyword not in ids:
                        msg = ('Field %s references unknown parent '
                               'keyword: %s' %
                               (tablefield.keyword, parent_keyword))
                        raise CriteriaError(msg)

                    if check_keyword not in ordered_ids:
                        ready = False
                        break

            if not ready:
                if last_not_ready_id == id_:
                    unprocessed_ids.append(id_)
                    raise CriteriaError(('Failed to resolve all field, '
                                         'may have circular dependencies: %s') %
                                        ([str(i) for i in unprocessed_ids]))
                elif last_not_ready_id is None:
                    last_not_ready_id = id_

                # Add this back to the list
                unprocessed_ids.append(id_)
            else:
                ordered_ids.append(id_)
                last_not_ready_id = None

        return ordered_ids

    def dynamic_fields(self):
        """Return dynamic, non-hidden fields."""
        return [self[id_] for id_, tablefield in self._tablefields.iteritems()
                if tablefield.dynamic and id_ in self.fields]

    def as_text(self):
        """ Return certain field values as a dict for simple json parsing
        """
        result = {}

        for k, v in self.cleaned_data.iteritems():

            if isinstance(v, datetime.datetime):
                result[k] = v.isoformat()
            elif isinstance(v, datetime.timedelta):
                result[k] = str(timedelta_total_seconds(v)) + " seconds"
            elif isinstance(v, UploadedFile):
                # look for uploaded files, save them off to another
                # temporary file and return the path for use in JSON
                # consumers of this file will need to clean them up
                # TODO this will be replaced by the File Storage App
                newtemp = tempfile.NamedTemporaryFile(delete=False)
                v.seek(0)
                shutil.copyfileobj(v, newtemp)
                v.close()
                newtemp.close()
                result[k] = newtemp.name
            else:
                result[k] = v

        return result

    def criteria(self):
        """ Return a Criteria object based on this form data. """

        if not self.is_valid():
            raise ValidationError("Form data is not valid")

        data = copy.copy(self.initial)
        for k, v in self.cleaned_data.iteritems():
            if k in (self._hidden_fields or []):
                data[k] = self.fields[k].clean(self._tablefields[k].initial)
            else:
                data[k] = v
        criteria = Criteria(**data)

        for id_ in self.compute_field_precedence():
            tablefield = self._tablefields[id_]

            if tablefield.post_process_template:
                # Resolve the fields criteria value by the <string>.format()
                # function using a template.
                try:
                    criteria[tablefield.keyword] = \
                        tablefield.post_process_template.format(**criteria)
                except:
                    msg = ("Failed to resolve field %s template: %s" %
                           (tablefield.keyword,
                            tablefield.post_process_template))
                    raise CriteriaTemplateError(msg)

            elif tablefield.post_process_func is not None:
                # Call the post process function
                func = tablefield.post_process_func
                try:
                    func(self, tablefield.keyword, criteria)
                except Exception as e:
                    msg = ('Field %s function %s raised an exception: %s %s' %
                           (tablefield, str(func), type(e), e))
                    raise CriteriaPostProcessError(msg)

                if tablefield.keyword not in criteria:
                    msg = ('Field %s function %s failed to set '
                           'criteria.%s value' %
                           (tablefield, str(func), tablefield.keyword))
                    raise CriteriaPostProcessError(msg)
            elif tablefield.keyword not in criteria:
                raise CriteriaError('Field %s has no value and no post-process '
                                    'function or template' %
                                    tablefield)

        return criteria

    def is_valid(self, check_unknown=False):
        super(TableFieldForm, self).is_valid()

        if check_unknown and self.is_bound:
            for k in self.data.keys():
                if k not in self.fields:
                    self._errors[k] = self.error_class(['Unknown criteria field'])

        return self.is_bound and not bool(self.errors)

    def apply_timezone(self, tzinfo):
        """ Apply `tzinfo` as the timezone of any naive datetime objects. """
        if not self.is_valid():
            raise ValidationError("Form data is not valid")

        for k, v in self.cleaned_data.iteritems():
            if isinstance(v, datetime.datetime) and v.tzinfo is None:
                self.cleaned_data[k] = v.replace(tzinfo=tzinfo)

    def get_tablefield(self, id):
        return self._tablefields[id]

    def get_field_value(self, keyword, fromfield_id):
        trykeywords = []

        m = re.match('(__s[0-9]_)', fromfield_id)
        if m:
            s = m.group(1)
            trykeywords.append(s + keyword)

        trykeywords.append(keyword)

        for k in trykeywords:
            if self.data and k in self.data:
                return self.data[k]

            if self.initial and k in self.initial:
                return self.initial[k]

        raise KeyError('Could not get a value for keyword: %s' % keyword)
