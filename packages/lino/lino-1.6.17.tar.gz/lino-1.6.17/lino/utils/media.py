# -*- coding: UTF-8 -*-
# Copyright 2013-2014 Luc Saffre
# License: BSD (see file COPYING for details)

import os

from django.conf import settings

davlink = settings.SITE.plugins.get('davlink', None)
has_davlink = davlink is not None and settings.SITE.use_java


class MediaFile(object):

    """
    Represents a file on the server with two properties `name` and `url`,
    using
    :setting:`MEDIA_ROOT`
    :attr:`use_davlink <ad.Site.use_davlink>`
    :attr:`webdav_root <ad.Site.webdav_root>`
    :attr:`webdav_url <ad.Site.webdav_url>`
    """

    def __init__(self, editable, *parts):
        self.editable = editable
        self.parts = parts

    @property
    def name(self):
        "return the filename on the server"
        if self.editable and has_davlink:
            return os.path.join(settings.SITE.webdav_root, *self.parts)
        return os.path.join(settings.MEDIA_ROOT, *self.parts)

    @property
    def url(self):
        "return the url that points to file on the server"
        if self.editable and has_davlink:
            return settings.SITE.webdav_url + "/".join(self.parts)
        return settings.SITE.build_media_url(*self.parts)


class TmpMediaFile(MediaFile):

    def __init__(self, ar, fmt):
        ip = ar.request.META.get('REMOTE_ADDR', 'unknown_ip')
        super(TmpMediaFile, self).__init__(False, 'cache',
                                           'appy' + fmt, ip, str(ar.actor) + '.' + fmt)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
