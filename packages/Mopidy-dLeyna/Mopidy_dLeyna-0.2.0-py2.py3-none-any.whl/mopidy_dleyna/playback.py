from __future__ import unicode_literals

import dbus

from mopidy import backend

from .dleyna import MEDIA_ITEM_IFACE, SERVER_BUS_NAME


class dLeynaPlaybackProvider(backend.PlaybackProvider):

    def __init__(self, audio, backend):
        super(dLeynaPlaybackProvider, self).__init__(audio, backend)
        self.__bus = dbus.SessionBus()

    def translate_uri(self, uri):
        _, _, path = uri.partition(':')
        obj = self.__bus.get_object(SERVER_BUS_NAME, path)
        props = dbus.Interface(obj, dbus.PROPERTIES_IFACE)
        urls = props.Get(MEDIA_ITEM_IFACE, 'URLs')
        return urls[0]
