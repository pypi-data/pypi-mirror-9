# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext import ndb
from gaegraph.model import Node, Arc
from gaeforms.ndb import property


class BlobFile(Node):
    filename = ndb.StringProperty(required=True)
    content_type = ndb.StringProperty(required=True)
    size = ndb.IntegerProperty(required=True)
    md5 = ndb.StringProperty(required=True)
    blob_key = ndb.BlobKeyProperty(required=True)
    img_url = ndb.TextProperty(default=None)  # Used only for images

    def img(self, size=None):
        if self.img_url == '':
            return ''
        if size is None:
            return self.img_url
        return '%s=s%s' % (self.img_url, size)


class OwnerToBlob(Arc):
    destination = ndb.KeyProperty(BlobFile)