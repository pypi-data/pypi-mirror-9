# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from rest_framework import serializers

from steelscript.appfwk.apps.devices.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
