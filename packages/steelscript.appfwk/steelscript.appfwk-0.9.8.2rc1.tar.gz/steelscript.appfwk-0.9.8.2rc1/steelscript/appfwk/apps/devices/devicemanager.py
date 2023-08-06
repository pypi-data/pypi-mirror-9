# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import logging
import importlib
import threading

from steelscript.appfwk.apps.plugins import plugins

from steelscript.common import UserAuth
from steelscript.appfwk.apps.devices.models import Device
from steelscript.appfwk.apps.devices.exceptions import DeviceModuleNotFound


logger = logging.getLogger(__name__)

lock = threading.Lock()


class DeviceManager(object):
    # map of active devices by datasource_id
    devices = {}

    @classmethod
    def clear(cls, device_id=None):
        if device_id and device_id in cls.devices:
            del cls.devices[device_id]
        else:
            cls.devices = {}

    @classmethod
    def get_device(cls, device_id):
        ds = Device.objects.get(id=device_id)

        with lock:
            if ds.id not in cls.devices:
                for module, pkg in plugins.devices():
                    if ds.module == module:
                        i = importlib.import_module(pkg)
                        break
                else:
                    msg = 'Module %s for device %s not found.' % (ds.module,
                                                                  ds.name)
                    raise DeviceModuleNotFound(msg)

                create_func = i.new_device_instance

                logger.debug("Creating new Device: %s(%s:%s)" % (ds.module,
                                                                 ds.host,
                                                                 ds.port))
                cls.devices[ds.id] = create_func(host=ds.host, port=ds.port,
                                                 auth=UserAuth(ds.username,
                                                               ds.password))
        return cls.devices[ds.id]

    @classmethod
    def get_modules(cls):
        """ Returns list of device modules. """
        return [module for module, pkg in plugins.devices()]
