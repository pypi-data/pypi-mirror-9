from __future__ import unicode_literals

import logging
import os

from mopidy import config, exceptions, ext

__version__ = '0.3.0'

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-dLeyna'
    ext_name = 'dleyna'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        return schema

    def setup(self, registry):
        from .backend import dLeynaBackend
        registry.add('backend', dLeynaBackend)

    def validate_environment(self):
        from .dleyna import MANAGER_IFACE, SERVER_BUS_NAME, SERVER_ROOT_PATH
        try:
            import dbus
        except ImportError as e:
            raise exceptions.ExtensionError('dbus library not found', e)
        try:
            bus = dbus.SessionBus()
        except Exception as e:
            raise exceptions.ExtensionError('cannot create session bus', e)
        try:
            obj = bus.get_object(SERVER_BUS_NAME, SERVER_ROOT_PATH)
            mgr = dbus.Interface(obj, MANAGER_IFACE)
        except Exception as e:
            raise exceptions.ExtensionError('dleyna-server not found', e)
        logger.info('%s/dleyna-server %s', self.dist_name, mgr.GetVersion())
