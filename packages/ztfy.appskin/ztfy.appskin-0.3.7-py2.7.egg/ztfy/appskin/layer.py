### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.bootstrap.layer import IBootstrapLayer, IBootstrapSkin

# import Zope3 packages
from zope.schema import TextLine

# import local packages

from ztfy.appskin import _


class IAppLayer(IBootstrapLayer):
    """Application base layer"""


class IAppSkin(IAppLayer, IBootstrapSkin):
    """Application base skin"""

    label = TextLine(title=_("ZTFY application skin"))
