##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
import doctest

import persistent

import zope.interface
import zope.schema
import zope.location.interfaces
from zope.container import contained
from zope.schema.fieldproperty import FieldProperty

import z3c.form.field

#import z3c.jsonrpc.testing
from j01.jsonrpc import jsform
from j01.jsonrpc import testing


class IDemoContent(zope.location.interfaces.IContained):
    """Demo content interface."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title')

    description = zope.schema.TextLine(
        title=u'Description',
        description=u'The description')


class DemoContent(persistent.Persistent, contained.Contained):
    """Demo content."""
    zope.interface.implements(IDemoContent)

    title = FieldProperty(IDemoContent['title'])
    description = FieldProperty(IDemoContent['description'])


class DemoForm(jsform.JSONRPCEditForm):
    """Sample JSON form."""

    fields = z3c.form.field.Fields(IDemoContent).select(
        'title', 'description')


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        testing.FunctionalDocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
