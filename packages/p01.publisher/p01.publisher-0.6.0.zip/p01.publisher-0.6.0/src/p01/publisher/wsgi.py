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
"""WSGI components

$Id: wsgi.py 3903 2013-12-20 03:45:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os.path

from p01.publisher.application import getWSGIApplication


def application_factory(global_conf, zope_conf=None, **local_conf):
    if zope_conf is not None:
        # You can simply define a zope_conf argument in your
        # paste.ini file app section like:
        # [app:zope]
        # use = egg:p01.publisher#app
        # zope_conf = app-zope.conf
        configfile = os.path.join(global_conf['here'], zope_conf)
    else:
        # or use p01.recipe.setup:paste which uses the following
        # name convention for generate the config files:
        # <part-name>-paste.ini 
        # <part-name>-zope.conf 
        # <part-name>-site.zcml
        # get <part-name> given from buildout recipe
        pasteName = os.path.basename(global_conf['__file__'])
        # find related zope.conf using the same <part-name>
        confName = '%szope.conf' % pasteName[:-len('paste.ini')]
        confPath = os.path.join(global_conf['here'], confName)
        if os.path.isfile(confPath):
            configfile = confPath
        else:
            # try default zope.conf as zope_conf name
            confPath = os.path.join(global_conf['here'], 'zope.conf')
            if os.path.isfile(confPath):
                configfile = confPath
            else:
                raise ValueError(
                    "Can't find paster zope.conf file for p01.publisher.wsgi")
    schemafile = os.path.join(os.path.dirname(__file__), 'schema', 'schema.xml')
    global APPLICATION
    APPLICATION = getWSGIApplication(configfile, schemafile)
    return APPLICATION
