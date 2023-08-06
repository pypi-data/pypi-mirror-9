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
"""Code to initialize the application server

$Id: appsetup.py 3903 2013-12-20 03:45:39Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component.hooks
from zope.security.interfaces import IParticipation
from zope.security.management import system_user

class SystemConfigurationParticipation(object):
    zope.interface.implements(IParticipation)

    principal = system_user
    interaction = None


_configured = False
def config(file, features=(), execute=True):
    r"""Execute the ZCML configuration file.

    This procedure defines the global site setup. Optionally you can also
    provide a list of features that are inserted in the configuration context
    before the execution is started.

    Let's create a trivial sample ZCML file.

      >>> import tempfile
      >>> fn = tempfile.mktemp('.zcml')
      >>> zcml = open(fn, 'w')
      >>> zcml.write('''
      ... <configure xmlns:meta="http://namespaces.zope.org/meta"
      ...            xmlns:zcml="http://namespaces.zope.org/zcml">
      ...   <meta:provides feature="myFeature" />
      ...   <configure zcml:condition="have myFeature2">
      ...     <meta:provides feature="myFeature4" />
      ...   </configure>
      ... </configure>
      ... ''')
      >>> zcml.close()

    We can now pass the file into the `config()` function:

      # End an old interaction first
      >>> from zope.security.management import endInteraction
      >>> endInteraction()

      >>> context = config(fn, features=('myFeature2', 'myFeature3'))
      >>> context.hasFeature('myFeature')
      True
      >>> context.hasFeature('myFeature2')
      True
      >>> context.hasFeature('myFeature3')
      True
      >>> context.hasFeature('myFeature4')
      True

    Further, we should have access to the configuration file name and context
    now:

      >>> getConfigSource() is fn
      True
      >>> getConfigContext() is context
      True

    Let's now clean up by removing the temporary file:

      >>> import os
      >>> os.remove(fn)

    """
    global _configured
    global __config_source
    __config_source = file

    if _configured:
        return

    from zope.configuration import xmlconfig, config

    # Set user to system_user, so we can do anything we want
    from zope.security.management import newInteraction
    newInteraction(SystemConfigurationParticipation())

    # Hook up custom component architecture calls
    zope.component.hooks.setHooks()

    # Load server-independent site config
    context = config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    for feature in features:
        context.provideFeature(feature)
    context = xmlconfig.file(file, context=context, execute=execute)

    # Reset user
    from zope.security.management import endInteraction
    endInteraction()

    _configured = execute

    global __config_context
    __config_context = context

    return context

__config_context = None
def getConfigContext():
    return __config_context

__config_source = None
def getConfigSource():
    return __config_source

def reset():
    global _configured
    _configured = False

    global __config_source
    __config_source = None

    global __config_context
    __config_context = None

try:
    import zope.testing.cleanup
except ImportError:
    pass
else:
    zope.testing.cleanup.addCleanUp(reset)
