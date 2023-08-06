# -*- coding: utf-8 -*-
from plone import api


def testSetup(context):
    if context.readDataFile('collective.atomrss.testing.txt') is None:
        return
