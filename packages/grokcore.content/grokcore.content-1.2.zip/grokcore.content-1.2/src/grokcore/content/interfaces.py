##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
"""Specific content interfaces for Grok.
"""
from grokcore.component.interfaces import IContext
from zope.container.interfaces import IOrderedContainer
from zope.container.interfaces import IContainer as IContainerBase
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent import ObjectModifiedEvent
import zope.interface


class IContainer(IContext, IContainerBase):
    """A Grok container.
    """


class IOrderedContainer(IContainer, IOrderedContainer):
    """A Grok container that can be ordered.
    """


class IObjectEditedEvent(IObjectModifiedEvent):
    """One of the attributes of the object was modified.
    """


class ObjectEditedEvent(ObjectModifiedEvent):
    zope.interface.implements(IObjectEditedEvent)
