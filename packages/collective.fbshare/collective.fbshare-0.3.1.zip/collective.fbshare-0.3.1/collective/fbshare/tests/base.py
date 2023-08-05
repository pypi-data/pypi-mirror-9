# -*- coding: utf-8 -*-

import unittest

from zope import interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from collective.fbshare.interfaces import IFbShareBrowserLayer, IFbShareSettings

class BaseTestCase(unittest.TestCase):
    
    def getSettings(self):
        registry = queryUtility(IRegistry)
        return registry.forInterface(IFbShareSettings, check=False)

    def markRequestWithLayer(self):
        # to be removed when p.a.testing will fix https://dev.plone.org/ticket/11673
        request = self.layer['request']
        interface.alsoProvides(request, IFbShareBrowserLayer)

