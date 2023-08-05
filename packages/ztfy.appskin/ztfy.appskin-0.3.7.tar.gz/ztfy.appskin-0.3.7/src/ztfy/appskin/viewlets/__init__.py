### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.i18n import translate
from zope.interface import implements
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.viewlet.manager import WeightOrderedViewletManager

# import local packages
from ztfy.appskin.interfaces import ITableActionsViewletManager, ITableActionViewlet
from ztfy.skin.viewlet import ViewletBase


class TableActionsViewletManager(WeightOrderedViewletManager):
    """Table actions viewlet manager"""

    implements(ITableActionsViewletManager)


class TableActionViewlet(ViewletBase):
    """Table action viewlet"""

    implements(ITableActionViewlet)

    def render(self):
        return '''<div class="btn btn-small btn-warning" onclick="$.ZTFY.dialog.open('%s/%s');">%s</div>''' % \
               (absoluteURL(self.context, self.request), self.target, translate(self.label, context=self.request))

