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
"""Publication

$Id: publication.py 4109 2014-08-19 11:47:11Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys
import logging
from new import instancemethod

import transaction

import zope.component
import zope.component.hooks
import zope.event
import zope.location
import zope.security.checker
import zope.security.management
from zope.browser.interfaces import ISystemErrorView
from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.authentication.interfaces import IFallbackUnauthenticatedPrincipal
from zope.authentication.interfaces import IAuthentication
from zope.error.interfaces import IErrorReportingUtility
from zope.publisher.publish import mapply
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.defaultview import queryDefaultViewName
from zope.publisher.interfaces import EndRequestEvent
from zope.publisher.interfaces import StartRequestEvent
from zope.publisher.interfaces import IExceptionSideEffects
from zope.publisher.interfaces import IHeld
from zope.publisher.interfaces import IPublication
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import Retry
from zope.security.management import newInteraction
from zope.security.management import endInteraction
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.traversing.interfaces import TraversalError
from zope.traversing.interfaces import BeforeTraverseEvent
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse

from p01.publisher import interfaces
from p01.publisher import publisher


##############################################################################
#
# helper

class Cleanup(object):
    """Hook for cleanup on request.close() call"""

    zope.interface.implements(IHeld)

    def __init__(self, f):
        self._f = f

    def release(self):
        self._f()
        self._f = None

    def __del__(self):
        if self._f is not None:
            logging.getLogger('SiteError').error(
                "Cleanup without request close")
            self._f()


def tryToLogException(arg1, arg2=None):
    """Dispatch to exception logger"""
    if arg2 is None:
        subsystem = 'SiteError'
        message = arg1
    else:
        subsystem = arg1
        message = arg2
    try:
        logging.getLogger(subsystem).exception(message)
    # Bare except, because we want to swallow any exception raised while
    # logging an exception.
    except:
        pass


def tryToLogWarning(arg1, arg2=None, exc_info=False):
    """Dispatch to warning logger"""
    if arg2 is None:
        subsystem = 'SiteError'
        message = arg1
    else:
        subsystem = arg1
        message = arg2
    try:
        logging.getLogger(subsystem).warn(message, exc_info=exc_info)
    # Bare except, because we want to swallow any exception raised while
    # logging a warning.
    except:
        pass


##############################################################################
#
# publication

zope.interface.implementer(interfaces.IPublication)
class Publication(object):
    """Base Zope publication specification

    NOTE: The BrowserPublication will start the transaction in the
    beforeTraversal method. See startRequest for more info.

    Note: You could implement your own publication class and use them in a
    IPublicationFactory and register this factory as p01:publisher or you can
    use the BrowserPublication and BrowserFactory defined below.

    Note: This implementation does not provide an authentication call after
    each traversal step. This publicationn concept only provides authentication
    at the wsgi application (root) level which is common for wsgi applications.
    If you need to implement placefull authentication, simply register an
    BeforeTraverseEvent event subscriber which get notified after every
    traversal step and authenticate the user as usual. But of corse this has
    nothing to do with local permissions. Placefull authentication only means
    you could support different authentication utilities at every traversal
    step.

    Take care, a publication instance is cached as a singleton in the
    IRequestProducer cache
    """

    def __init__(self, app):
        """initialize publication with given wsgi application"""
        self.app = app

    @property
    def _auth(self):
        """Knows how to get the IAuthentication utility.

        Simply override this in your own publication and provide your own
        authentication concept providing the IAuthentication api
        """
        sm = self.app.getSiteManager()
        return sm.queryUtility(IAuthentication)

    def getApplication(self, request):
        """Returns the zope wsgi applicaton (root)."""
        return zope.security.checker.ProxyFactory(self.app)

    def proxy(self, ob):
        """Security-proxy an object

        Subclasses may override this to use a different proxy (or
        checker) implementation or to not proxy at all.
        """
        return zope.security.checker.ProxyFactory(ob)

    # publish stack
    def startRequest(self, request):
        """Start new interaction and beginn transaction.

        The startRequest allows us to prepare everything and handle
        request.processInputs with transaction control.
        """
        # set site hook
        zope.component.hooks.setSite(self.app)
        # notify start request
        zope.event.notify(StartRequestEvent(request))
        # start transaction
        transaction.begin()

    def beforeTraversal(self, request):
        """Authenticate and set principal

        Note, we allready started the transaction
        """
        # authenticate after we called processInputs
        auth = self._auth
        principal = auth.authenticate(request)
        if principal is None:
            principal = auth.unauthenticatedPrincipal()
            if principal is None:
                # Get the fallback unauthenticated principal
                principal = zope.component.getUtility(
                    IFallbackUnauthenticatedPrincipal)

        # set principal
        request.setPrincipal(principal)
        # start new interaction
        zope.security.management.newInteraction(request)

    def callTraversalHooks(self, request, ob):
        # notify before traverse event. There is no need for authenticate
        zope.event.notify(BeforeTraverseEvent(ob, request))

    def traverseName(self, request, ob, name):
        nm = name # the name to look up the object with

        if name and name[:1] in '@+':
            # Process URI segment parameters.
            ns, nm = nsParse(name)
            if ns:
                try:
                    ob2 = namespaceLookup(ns, nm, ob, request)
                except TraversalError:
                    raise NotFound(ob, name)

                return self.proxy(ob2)

        if nm == '.':
            return ob

        if IPublishTraverse.providedBy(ob):
            ob2 = ob.publishTraverse(request, nm)
        else:
            # self is marker
            adapter = zope.component.queryMultiAdapter((ob, request),
                IPublishTraverse, default=self)
            if adapter is not self:
                ob2 = adapter.publishTraverse(request, nm)
            else:
                raise NotFound(ob, name, request)

        return self.proxy(ob2)

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def callErrorView(self, request, view):
        # We don't want to pass positional arguments.  The positional
        # arguments were meant for the published object, not an exception
        # view.
        return mapply(view, (), request)

    def afterCall(self, request, ob):
        txn = transaction.get()
        if txn.isDoomed():
            txn.abort()
        else:
            self.annotateTransaction(txn, request, ob)
            txn.commit()

    def endRequest(self, request, ob):
        zope.event.notify(EndRequestEvent(ob, request))
        endInteraction()
        zope.component.hooks.setSite(None)

    # transaction helper
    def annotateTransaction(self, txn, request, ob):
        """Set some useful meta-information on the transaction. This
        information is used by the undo framework, for example.

        This method is not part of the `IPublication` interface, since
        it's specific to this particular implementation.
        """
        if request.principal is not None:
            txn.setUser(request.principal.id)

        # Work around methods that are usually used for views
        bare = removeSecurityProxy(ob)
        if isinstance(bare, instancemethod):
            ob = bare.im_self

        # set the location path
        path = None
        locatable = IPhysicallyLocatable(ob, None)
        if locatable is not None:
            # Views are made children of their contexts, but that
            # doesn't necessarily mean that we can fully resolve the
            # path. E.g. the family tree of a resource cannot be
            # resolved completely, as the site manager is a dead end.
            try:
                path = locatable.getPath()
            except (AttributeError, TypeError):
                pass
        if path is not None:
            txn.setExtendedInfo('location', path)

        # set the request type
        iface = IRequest
        for iface in zope.interface.providedBy(request):
            if iface.extends(IRequest):
                break

        # apply request_type
        iface_dotted = iface.__module__ + '.' + iface.getName()
        txn.setExtendedInfo('request_type', iface_dotted)
        # apply request_info
        request_info = request.method + ' ' + request.getURL()
        txn.setExtendedInfo('request_info', request_info)
        return txn

    # error handling
    def _logErrorWithErrorReportingUtility(self, object, request, exc_info):
        # Record the error with the ErrorReportingUtility
        self.beginErrorHandlingTransaction(request, object,
                                           'error reporting utility')
        try:
            errUtility = zope.component.getUtility(IErrorReportingUtility)

            # It is important that an error in errUtility.raising
            # does not propagate outside of here. Otherwise, nothing
            # meaningful will be returned to the user.
            #
            # The error reporting utility should not be doing database
            # stuff, so we shouldn't get a conflict error.
            # Even if we do, it is more important that we log this
            # error, and proceed with the normal course of events.
            # We should probably (somehow!) append to the standard
            # error handling that this error occurred while using
            # the ErrorReportingUtility, and that it will be in
            # the zope log.

            errUtility.raising(exc_info, request)
            transaction.commit()
        except:
            tryToLogException(
                'Error while reporting an error to the Error Reporting utility'
                )
            transaction.abort()

    def handleException(self, object, request, exc_info):
        # This transaction had an exception that reached the publisher.
        # It must definitely be aborted.
        try:
            transaction.abort()
        except:
            # Hm, a catastrophe.  We might want to know what preceded it.
            self._logErrorWithErrorReportingUtility(object, request, exc_info)
            # this forces to propagate the error to wsgi. That's not what we
            # like to do, But what else should we do here? Should force to
            # render a nicer 500 error mesage based on a view?
            raise

        # Record the error with the ErrorReportingUtility.
        self._logErrorWithErrorReportingUtility(object, request, exc_info)

        # prepare error response (find a view for a known error)
        response = request.response
        response.reset()
        exception = None
        legacy_exception = not isinstance(exc_info[1], Exception)
        if legacy_exception:
            response.handleException(exc_info)
            if isinstance(exc_info[1], str):
                tryToLogWarning(
                    'Publisher received a legacy string exception: %s.'
                    ' This will be handled by the request.' %
                    exc_info[1])
            else:
                tryToLogWarning(
                    'Publisher received a legacy classic class exception: %s.'
                    ' This will be handled by the request.' %
                    exc_info[1].__class__)
        else:
            # We definitely have an Exception
            # Set the request body, and abort the current transaction.
            self.beginErrorHandlingTransaction(
                request, object, 'application error-handling')
            view = None
            try:
                # We need to get a location, because some template content of
                # the exception view might require one.
                #
                # The object might not have a parent, because it might be a
                # method. If we don't have a `__parent__` attribute but have
                # an im_self or a __self__, use it.
                loc = object
                if not hasattr(object, '__parent__'):
                    loc = removeSecurityProxy(object)
                    # Try to get an object, since we apparently have a method
                    # Note: We are guaranteed that an object has a location,
                    # so just getting the instance the method belongs to is
                    # sufficient.
                    loc = getattr(loc, 'im_self', loc)
                    loc = getattr(loc, '__self__', loc)
                    # Protect the location with a security proxy
                    loc = self.proxy(loc)

                # Give the exception instance its location and look up the
                # view.
                exception = zope.location.LocationProxy(exc_info[1], loc, '')
                name = queryDefaultViewName(exception, request)
                if name is not None:
                    view = zope.component.queryMultiAdapter(
                        (exception, request), name=name)
            except:
                # Problem getting a view for this exception. Log an error.
                tryToLogException(
                    'Exception while getting view on exception')


            if view is not None:
                try:
                    body = self.callErrorView(request, view)
                    response.setResult(body)
                    transaction.commit()
                    if (ISystemErrorView.providedBy(view)
                        and view.isSystemError()):
                        # Got a system error, want to log the error

                        # Lame hack to get around logging missfeature
                        # that is fixed in Python 2.4
                        try:
                            raise exc_info[0], exc_info[1], exc_info[2]
                        except:
                            logging.getLogger('SiteError').exception(
                                str(request.URL),
                                )

                except:
                    # Problem rendering the view for this exception.
                    # Log an error.
                    tryToLogException(
                        'Exception while rendering view on exception')

                    # Record the error with the ErrorReportingUtility
                    self._logErrorWithErrorReportingUtility(
                        object, request, sys.exc_info())

                    view = None

            if view is None:
                # Either the view was not found, or view was set to None
                # because the view couldn't be rendered. In either case,
                # we let the request handle it.
                response.handleException(exc_info)
                transaction.abort()

    def beginErrorHandlingTransaction(self, request, ob, note):
        txn = transaction.begin()
        txn.note(note)
        self.annotateTransaction(txn, request, ob)
        return txn


###############################################################################
#
# browser

class BrowserPublication(Publication):
    """Browser publication"""

    zope.interface.implements(interfaces.IBrowserPublication)

    def getDefaultTraversal(self, request, ob):
        if IBrowserPublisher.providedBy(ob):
            # ob is already proxied, so the result of calling a method will be
            return ob.browserDefault(request)
        else:
            adapter = zope.component.queryMultiAdapter((ob, request),
                IBrowserPublisher)
            if adapter is not None:
                ob, path = adapter.browserDefault(request)
                ob = self.proxy(ob)
                return ob, path
            else:
                # ob is already proxied
                return ob, None

    def afterCall(self, request, ob):
        super(BrowserPublication, self).afterCall(request, ob)
        if request.method == 'HEAD':
            request.response.setResult('')


###############################################################################
#
# json-rpc

class JSONRPCPublication(Publication):
    """JSON-RPC publication"""

    zope.interface.implements(interfaces.IJSONRPCPublication)
