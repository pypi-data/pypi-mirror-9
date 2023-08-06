# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from django import forms

from steelscript.netprofiler.core import _constants
from steelscript.appfwk.apps.devices.models import Device


def get_device_choices(device_type):
    devices = Device.objects.filter(module=device_type, enabled=True)
    return [(d.id, d.name) for d in devices]


def get_groupbys():
    return [('', '---')] + sorted(((v, k) for k,v in _constants.groupbys.iteritems()))


def get_realms():
    return [('', '---')] + [(c, c.title().replace('_', ' ')) for c in _constants.realms]


def get_centricities():
    return ('', '---'), ('hos', 'host'), ('int', 'interface')


class DeviceInputForm(forms.Form):
    def valid_devices(self):
        return len(self.fields['device'].choices) > 0


class NetProfilerInputForm(DeviceInputForm):
    realm = forms.ChoiceField(choices=get_realms())
    centricity = forms.ChoiceField(choices=get_centricities())
    groupby = forms.ChoiceField(choices=get_groupbys())

    def __init__(self, *args, **kwargs):
        super(NetProfilerInputForm, self).__init__(*args, **kwargs)
        cf = forms.ChoiceField(choices=get_device_choices('netprofiler'))
        self.fields.insert(0, 'device', cf)


class NetSharkInputForm(DeviceInputForm):
    def __init__(self, *args, **kwargs):
        super(NetSharkInputForm, self).__init__(*args, **kwargs)
        cf = forms.ChoiceField(choices=get_device_choices('netshark'))
        self.fields.insert(0, 'device', cf)
