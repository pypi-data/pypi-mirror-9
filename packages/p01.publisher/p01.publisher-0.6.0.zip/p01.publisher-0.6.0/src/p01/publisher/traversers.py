##############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
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
"""Object traversers

$Id: traversers.py 4109 2014-08-19 11:47:11Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.defaultview import getDefaultViewName


class SimpleComponentTraverser(object):
    """Browser traverser for simple components that can only traverse to views
    """
    zope.interface.implements(IBrowserPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def browserDefault(self, request):
        ob = self.context
        if request.method == 'OPTIONS':
            # support OPTIONS CORS preflight and use OPTIONS view
            view_name = 'OPTIONS'
        else:
            view_name = getDefaultViewName(ob, request)
        return ob, (view_name,)

    def publishTraverse(self, request, name):
        ob = self.context
        view = zope.component.queryMultiAdapter((ob, request), name=name)
        if view is None:
            raise NotFound(ob, name)
        return view


class FileContentTraverser(SimpleComponentTraverser):
    """Browser traverser for file content.

    The default view for file content has effective URLs that don't end in
    /.  In particular, if the content inclused HTML, relative links in
    the HTML are relative to the container the content is in.
    """

    def browserDefault(self, request):
        ob = self.context

        view_name = getDefaultViewName(ob, request)
        view = self.publishTraverse(request, view_name)
        if hasattr(view, 'browserDefault'):
            if request.method == 'OPTIONS':
                # support OPTIONS CORS preflight and use OPTIONS view
                view_name = 'OPTIONS'
            else:
                view, path = view.browserDefault(request)
            if len(path) == 1:
                view = view.publishTraverse(request, path[0])
                path = ()
        else:
            path = ()

        return view, path


def NoTraverser(ob, request):
    return None
