# -*- coding: utf-8 -*-
from plone.rfc822.defaultfields import BaseFieldMarshaler
from plone.rfc822.interfaces import IFieldMarshaler
from zope import schema
from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
try:
    import json
except ImportError:
    import simplejson as json


@adapter(Interface, schema.Dict)
@implementer(IFieldMarshaler)
class DictionaryFieldMarshaller(BaseFieldMarshaler):
    ascii = True

    def encode(self, value, charset="utf-8", primary=False):
        if value:
            return json.dumps(value)
        else:
            return super(DictionaryFieldMarshaller, self).encode(
                value, charset=charset, primary=primary)

    # noinspection PyPep8Naming
    def decode(self, value, message=None, charset="utf-8",
               contentType=None, primary=False):
        if value:
            return json.loads(value)
        else:
            return super(DictionaryFieldMarshaller, self).decode(
                value, message=message, charset=charset,
                contentType=contentType, primary=primary)
