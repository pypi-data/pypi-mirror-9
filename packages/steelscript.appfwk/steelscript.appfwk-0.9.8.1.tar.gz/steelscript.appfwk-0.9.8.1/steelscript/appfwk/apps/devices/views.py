# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import logging

from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, views
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import DeviceListForm, DeviceDetailForm
from steelscript.appfwk.apps.devices.models import Device
from steelscript.appfwk.apps.devices.serializers import DeviceSerializer

logger = logging.getLogger(__name__)


class DeviceDetail(views.APIView):
    """ Display and update user preferences
    """
    model = Device
    serializer_class = DeviceSerializer
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    permission_classes = (IsAdminUser,)

    def get(self, request, device_id=None):
        if request.accepted_renderer.format == 'html':
            if device_id:
                device = get_object_or_404(Device, pk=device_id)
                form = DeviceDetailForm(instance=device)
            else:
                form = DeviceDetailForm()
            return Response({'form': form}, template_name='device_detail.html')
        else:
            device = get_object_or_404(Device, pk=device_id)
            serializer = DeviceSerializer(instance=device)
            data = serializer.data
            return Response(data)

    def post(self, request, device_id=None):
        if device_id:
            device = get_object_or_404(Device, pk=device_id)
            form = DeviceDetailForm(request.DATA, instance=device)
        else:
            form = DeviceDetailForm(request.DATA)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('device-list'))
        else:
            return Response({'form': form}, template_name='device_detail.html')

    def delete(self, request, device_id):
        device = get_object_or_404(Device, pk=device_id)
        device.delete()
        return HttpResponse(status=204)


class DeviceList(generics.ListAPIView):
    model = Device
    serializer_class = DeviceSerializer
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        queryset = Device.objects.order_by('id')
        invalid = request.QUERY_PARAMS.get('invalid', None)

        if request.accepted_renderer.format == 'html':
            DeviceFormSet = modelformset_factory(Device,
                                                 form=DeviceListForm,
                                                 extra=0)
            formset = DeviceFormSet(queryset=queryset)
            tabledata = zip(formset.forms, queryset)
            data = {'formset': formset, 'tabledata': tabledata,
                    'invalid': invalid}
            return Response(data, template_name='device_list.html')

        serializer = DeviceSerializer(instance=queryset)
        data = serializer.data
        return Response(data)

    def put(self, request, *args, **kwargs):
        """ Function to save changes to multiple devices once.

        This function is called only when the "Save Changes" button is
        clicked on /devices/ page. However, it only supports enable/disable
        device(s). The url sent out will only include 'enable' field.
        """
        DeviceFormSet = modelformset_factory(Device,
                                             form=DeviceListForm,
                                             extra=0)
        formset = DeviceFormSet(request.DATA)

        if formset.is_valid():
            formset.save()
            DeviceManager.clear()
            if '/devices' not in request.META['HTTP_REFERER']:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect(reverse('device-list'))

        else:
            data = {'formset': formset}
            return Response(data, template_name='device_list.html')
