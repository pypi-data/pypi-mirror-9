# -*- coding: utf-8 -*-
from zope.interface import implements
from Products.CMFPlone.interfaces import INonInstallable


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return ['collective.atomrss:uninstall']
