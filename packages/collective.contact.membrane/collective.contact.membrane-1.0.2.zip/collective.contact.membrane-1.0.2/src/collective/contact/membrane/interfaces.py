# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from collective.contact.membrane import _


class ICollectiveContactMembraneLayer(IDefaultBrowserLayer):

    """Marker interface that defines a browser layer."""


class IContactMembraneParameters(Interface):

    """Parameters for collective.contact.membrane product."""

    active_held_position_states = schema.List(
        title=_(u"Active states for held positions"),
        description=_(
            u"States of the held positions for which the person "
            "is member of the group."),
        required=False)
