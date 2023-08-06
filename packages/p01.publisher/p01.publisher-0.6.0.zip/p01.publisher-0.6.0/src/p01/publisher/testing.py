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
"""Testing support

$Id: testing.py 4149 2015-02-03 03:16:23Z roger.ineichen $
"""

import copy
import logging
import os.path
import re
import rfc822
import sys
import doctest
import contextlib
from cStringIO import StringIO

if sys.version_info[0] > 2:
    from http.cookies import SimpleCookie
else:
    from Cookie import SimpleCookie

import transaction

import zope.interface
import zope.component
import zope.component.testlayer
import zope.security.testing
import zope.security.management
from zope.component import hooks
from zope.publisher.browser import BrowserLanguages

import z3c.json.proxy
import z3c.json.transport
import z3c.json.exceptions
from z3c.jsonrpc.publisher import JSON_RPC_VERSION

import p01.publisher.application
import p01.publisher.interfaces
import p01.publisher.publisher
import p01.publisher.request
import p01.publisher.product
import p01.testbrowser.testing


# These interaction methods are enhanced versions of the ones in
# zope.security.testing . They use a TestRequest instead of a TestParticipation.

def create_interaction(principal_id, **kw):
    principal = zope.security.testing.Principal(principal_id, **kw)
    request = TestRequest()
    request.setPrincipal(principal)
    zope.security.management.newInteraction(request)
    return principal


@contextlib.contextmanager
def interaction(principal_id, **kw):
    if zope.security.management.queryInteraction():
        # There already is an interaction. Great. Leave it alone.
        yield
    else:
        principal = create_interaction(principal_id, **kw)
        try:
            yield principal
        finally:
            zope.security.management.endInteraction()


class IManagerSetup(zope.interface.Interface):
    """Utility for enabling up a functional testing manager with needed grants

    TODO This is an interim solution.  It tries to break the dependence
    on a particular security policy, however, we need a much better
    way of managing functional-testing configurations.
    """

    def setUpManager():
        """Set up the manager, zope.mgr
        """


def getRootFolder():
    return zope.component.getUtility(p01.publisher.interfaces.IApplication)


headerre = re.compile(r'(\S+): (.+)$')
def split_header(header):
    return headerre.match(header).group(1, 2)

basicre = re.compile('Basic (.+)?:(.+)?$')
def auth_header(header):
    match = basicre.match(header)
    if match:
        import base64
        u, p = match.group(1, 2)
        if u is None:
            u = ''
        if p is None:
            p = ''
        auth = base64.encodestring('%s:%s' % (u, p))
        return 'Basic %s' % auth[:-1]
    return header


class TestRequest(p01.publisher.request.BrowserRequest):
    """TestRequest which does not apply IDefaultBrowserLayer."""

    def __init__(self, body_instream=None, environ=None, form=None,
                 skin=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ is not None:
            _testEnv.update(environ)

        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            body_instream = StringIO('')

        super(TestRequest, self).__init__(body_instream, _testEnv)
        if form:
            self.form.update(form)

        # Setup locale object
        langs = BrowserLanguages(self).getPreferredLanguages()
        from zope.i18n.locales import locales
        if not langs or langs[0] == '':
            self._locale = locales.getLocale(None, None, None)
        else:
            parts = (langs[0].split('-') + [None, None])[:3]
            self._locale = locales.getLocale(*parts)

        if skin is not None:
            zope.interface.directlyProvides(self, skin)


class FunctionalTestSetup(object):
    """Keeps shared state across several functional test cases."""

    __shared_state = { '_init': False }

    def __init__(self, config_file=None, product_config=None):
        """Initializes Zope 3 framework and configuration files."""
        self.__dict__ = self.__shared_state

        if not self._init:
            if not config_file:
                config_file = 'ftesting.zcml'
            self.log = StringIO()
            # Make it silent but keep the log available for debugging
            logging.root.addHandler(logging.StreamHandler(self.log))

            self.old_product_config = copy.deepcopy(
                p01.publisher.product.saveConfiguration())
            configs = []
            if product_config:
                configs = p01.publisher.product.loadConfiguration(
                    StringIO(product_config))
                configs = [
                    p01.publisher.product.FauxConfiguration(name, values)
                    for name, values in configs.items()
                    ]
            self.local_product_config = configs
            p01.publisher.product.setProductConfigurations(configs)

            # This handles anything added by generations or other bootstrap
            # subscribers.
            transaction.commit()

            self._config_file = config_file
            self._product_config = product_config
            self._init = True

            # Make a local grant for the test user
            setup = zope.component.queryUtility(IManagerSetup)
            if setup is not None:
                setup.setUpManager()

        elif config_file and config_file != self._config_file:
            # Running different tests with different configurations is not
            # supported at the moment
            raise NotImplementedError('Already configured'
                                      ' with a different config file')

        elif product_config and product_config != self._product_config:
            raise NotImplementedError('Already configured'
                                      ' with different product configuration')

    def setUp(self):
        """Prepares for a functional test case."""
        # Tear down the old demo storages (if any) and create fresh ones
        transaction.abort()
        p01.publisher.product.setProductConfigurations(
            self.local_product_config)

    def tearDown(self):
        """Cleans up after a functional test case."""
        transaction.abort()
        hooks.setSite(None)

    def tearDownCompletely(self):
        """Cleans up the setup done by the constructor."""
        transaction.abort()
        p01.publisher.product.restoreConfiguration(
            self.old_product_config)
        self._config_file = False
        self._product_config = None
        self._init = False

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return getRootFolder()


def getWSGIApplication(app=None, useBasicAuth=True):
    """Retrun a plain simple p01.publisher wsgi application"""
    if app is None:
        app = zope.component.queryUtility(p01.publisher.interfaces.IApplication)
    if app is None:
        # fallback to a simple IApplication
        app = p01.publisher.application.Application()
    wsgi_app = p01.publisher.application.WSGIApplication(app)
    if useBasicAuth:
        wsgi_app = p01.testbrowser.testing.AuthorizationMiddleware(wsgi_app)
    return wsgi_app


class ZCMLLayer(p01.testbrowser.testing.Layer, zope.component.testlayer.ZCMLFileLayer):
    """ZCML-defined test layer supporting make_wsgi_app used for testbrowser"""

    __bases__ = ()
    __name__ = 'ZCMLLayer'

    def __init__(self, package, name=None, zcml_file='ftesting.zcml',
        product_config=None, make_wsgi_app=None, useBasicAuth=True):
        super(ZCMLLayer, self).__init__(package, zcml_file=zcml_file,
            name=None, features=None)
        self.product_config = product_config
        if make_wsgi_app is not None:
            # override with custom callable
            self.make_wsgi_app = make_wsgi_app
        self.useBasicAuth = useBasicAuth

    def make_wsgi_app(self):
        app = zope.component.queryUtility(p01.publisher.interfaces.IApplication)
        if app is None:
            # fallback to a simple IApplication
            app = p01.publisher.application.Application()
        wsgi_app = p01.publisher.application.WSGIApplication(app)
        if self.useBasicAuth:
            wsgi_app = p01.testbrowser.testing.AuthorizationMiddleware(wsgi_app)
        return wsgi_app

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        self.setup = FunctionalTestSetup(
            self.zcml_file, product_config=self.product_config)

    def tearDown(self):
        super(ZCMLLayer, self).tearDown()
        self.setup.tearDownCompletely()


def getZCMLLayer(pkgName, name, zcml='ftesting.zcml', product_config=None,
    make_wsgi_app=None):
    """Returns the ZCMLLayer based on package name."""
    package = sys.modules[pkgName]
    return ZCMLLayer(package, name=name,
#        zcml_file=os.path.join(os.path.dirname(globals['__file__']), zcml),
        zcml_file=zcml,
        product_config=product_config,
        make_wsgi_app=make_wsgi_app,
        )


def defineLayer(name, zcml='ftesting.zcml', product_config=None,
    make_wsgi_app=None):
    """Helper function for defining layers.

    Usage: defineLayer(my.package)

    ATTENTION: Don't use this helper method if a subprocess based setup is
    involved. Because our sys._getframe will get messed up by the subprocess
    call. This is the case with m01.stub and p01.elasitcsearch as an example.
    Use the plain ZCMLLayer class for define ftesting setup.
    """
    globals = sys._getframe(1).f_globals
    pkgName = globals['__package__']
    package = sys.modules[pkgName]
    globals[name] = ZCMLLayer(
        package,
        name=name,
#        zcml_file=os.path.join(os.path.dirname(globals['__file__']), zcml),
        zcml_file=zcml,
        product_config=product_config,
        make_wsgi_app=make_wsgi_app,
        )


def prepareDocTestKeywords(kw):
    globs = kw.setdefault('globs', {})
    if globs.get('getRootFolder') is None:
        globs['getRootFolder'] = getRootFolder

    kwsetUp = kw.get('setUp')
    def setUp(test):
        FunctionalTestSetup().setUp()
        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.NORMALIZE_WHITESPACE)


###############################################################################
#
# test browser
#
###############################################################################

def getTestBrowser(url=None, wsgi_app=None, handleErrors=True,
    useBasicAuth=True):
    """Get test browser"""
    if wsgi_app is None:
        app = zope.component.getUtility(p01.publisher.interfaces.IApplication)
        publisher = p01.publisher.publisher.Publisher
        wsgi_app = p01.publisher.application.WSGIApplication(app, publisher,
            handleErrors)
        if useBasicAuth:
            wsgi_app = p01.testbrowser.testing.AuthorizationMiddleware(
                wsgi_app)
    browser = p01.testbrowser.testing.Browser(url=url, wsgi_app=wsgi_app)
    browser.handleErrors = handleErrors
    return browser


###############################################################################
#
# JSONRPC Test proxy
#
###############################################################################

class ResponseWrapper(object):
    """A wrapper that adds several introspective methods to a response."""

    def __init__(self, response, path, omit=()):
        self._response = response
        self._path = path
        self.omit = omit
        self._body = None

    def getOutput(self):
        """Returns the full HTTP output (headers + body)"""
        body = self.getBody()
        omit = self.omit
        headers = [x
                   for x in self._response.getHeaders()
                   if x[0].lower() not in omit]
        headers.sort()
        headers = '\n'.join([("%s: %s" % (n, v)) for (n, v) in headers])
        statusline = '%s %s' % (self._response._request['SERVER_PROTOCOL'],
                                self._response.getStatusString())
        if body:
            return '%s\n%s\n\n%s' %(statusline, headers, body)
        else:
            return '%s\n%s\n' % (statusline, headers)

    def getBody(self):
        """Returns the response body"""
        if self._body is None:
            self._body = ''.join(self._response.consumeBody())

        return self._body

    def getPath(self):
        """Returns the path of the request"""
        return self._path

    def __getattr__(self, attr):
        return getattr(self._response, attr)

    __str__ = getOutput


class JSONRPCTestTransport(z3c.json.transport.Transport):
    """Test transport using wsgi application and it's publisher.

    It can be used like a normal transport, including support for basic
    authentication.
    """

    cookies = None
    verbose = False
    handleErrors = True

    def __init__(self, app):
        self.app = app
        # store cookies between consecutive requests
        self.cookies = SimpleCookie()

    # cookies
    def httpCookie(self, path):
         """Return self.cookies as an HTTP_COOKIE environment value."""
         l = [m.OutputString().split(';')[0] for m in self.cookies.values()
              if path.startswith(m['path'])]
         return '; '.join(l)

    def loadCookies(self, envstring):
        self.cookies.load(envstring)

    def saveCookies(self, response):
        """Save cookies from the response."""
        for k,v in response._cookies.items():
            k = k.encode('utf8')
            self.cookies[k] = v['value'].encode('utf8')
            if v.has_key('path'):
                self.cookies[k]['path'] = v['path']

    # request handling
    def request(self, host, handler, request_body, verbose=0):
        if not handler:
            handler = '/'
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: application/json-rpc\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"],)

        request += "\n" + request_body
        response = self.doRequest(request, handleErrors=self.handleErrors)
        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise z3c.json.exceptions.ProtocolError(host + handler, errcode,
                errmsg, headers)

        return self._parse_response(StringIO(response.getBody()), sock=None)

    def doPublish(self, instream, environment):
        """Publish input stream and return request"""
        request = self.app.publisher(instream, environment)
        return self.app.publisher.publish(request,
            handleErrors=self.handleErrors)

    def doRequest(self, request_string, handleErrors=True):
        """Process request and return response"""
        # commit work done by previous request
        transaction.commit()

        # discard leading white space to make call layout simpler
        request_string = request_string.lstrip()

        # split off and parse the command line
        l = request_string.find('\n')
        command_line = request_string[:l].rstrip()
        request_string = request_string[l+1:]
        method, path, protocol = command_line.split()

        instream = StringIO(request_string)
        environment = {"HTTP_COOKIE": self.httpCookie(path),
                       "HTTP_HOST": 'localhost',
                       "HTTP_REFERER": 'localhost',
                       "REQUEST_METHOD": method,
                       "SERVER_PROTOCOL": protocol,
                       }

        headers = [split_header(header)
                   for header in rfc822.Message(instream).headers]
        for name, value in headers:
            name = ('_'.join(name.upper().split('-')))
            if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                name = 'HTTP_' + name
            environment[name] = value.rstrip()

        auth_key = 'HTTP_AUTHORIZATION'
        if environment.has_key(auth_key):
            environment[auth_key] = auth_header(environment[auth_key])

        old_site = hooks.getSite()
        hooks.setSite(None)

        request = self.doPublish(instream, environment)

        response = ResponseWrapper(
            request.response, path,
            omit=('x-content-type-warning', 'x-powered-by'),
            )

        self.saveCookies(response)
        hooks.setSite(old_site)

        return response


def getJSONRPCTestProxy(uri, app=None, transport=None, encoding=None,
    verbose=None, jsonId=None, handleErrors=True, jsonVersion=JSON_RPC_VERSION):
    """Test JSONRPCProxy using wsgi app and it's publisher for processing"""
    if app is None:
        app = zope.component.getUtility(p01.publisher.interfaces.IApplication)
        publisher = p01.publisher.publisher.Publisher
        wsgi_app = p01.publisher.application.WSGIApplication(app, publisher,
            handleErrors)
    if verbose is None:
        verbose = 0
    if transport is None:
        transport = JSONRPCTestTransport(wsgi_app)
    if isinstance(transport, JSONRPCTestTransport):
        transport.handleErrors = handleErrors
    return z3c.json.proxy.JSONRPCProxy(uri, transport, encoding, verbose,
        jsonId, jsonVersion)
