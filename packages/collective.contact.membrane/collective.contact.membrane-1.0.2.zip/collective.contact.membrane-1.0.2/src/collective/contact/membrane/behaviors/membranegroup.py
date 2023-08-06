# -*- coding: utf8 -*-
"""Turn organizations into Membrane groups."""
from five import grok

from zc.relation.interfaces import ICatalog
from zope.component import getUtility, queryAdapter
from zope.intid.interfaces import IIntIds

from Products.membrane.interfaces import IGroup
from Products.membrane.interfaces.user import IMembraneUserGroups
from dexterity.membrane.behavior.membranegroup import IMembraneGroup as IOriginMembraneGroup
from dexterity.membrane.behavior.membranegroup import MembraneGroup as OriginMembraneGroup
from plone import api

from collective.contact.core.content.held_position import IHeldPosition


def get_active_states():
    """Return active states for held position."""
    record_name = "collective.contact.membrane.interfaces."\
                  "IContactMembraneParameters.active_held_position_states"
    try:
        active_states = api.portal.get_registry_record(record_name)
    except api.exc.InvalidParameterError:
        active_states = []

    return active_states


class IMembraneGroup(IOriginMembraneGroup):

    """Marker interface for Membrane Group."""


class MembraneGroup(OriginMembraneGroup):

    """Turn organizations into Membrane groups.

    If active states is empty, every person who have an held position in the
    organization is a group member.
    If active states is not empty, only persons that have an at least an
    held position in one of these states are group member.
    """

    def Title(self):
        """Return group title."""
        return self.context.Title()

    def getGroupId(self):
        """Concatenate all ids in the chain of organizations/positions."""
        chain = self.context.get_organizations_chain()
        return '_'.join([x.getId() for x in chain])

    def getGroupName(self):
        """Return group name."""
        return self.context.Title()

    def getGroupMembers(self):
        """Get persons object that are members of this group."""
        held_positions = self.getGroupHeldPositions()
        return tuple([hp.getParentNode().UID() for hp in held_positions])

    def getGroupHeldPositions(self):
        """Get held_positions objects in this group."""
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        intid = intids.queryId(self.context)
        held_positions = []
        active_states = get_active_states()
        query = {'to_id': intid,
                 'from_interfaces_flattened': IHeldPosition,
                 'from_attribute': 'position'}
        for relation in catalog.findRelations(query):
            held_position = relation.from_object
            if (not active_states
                    or api.content.get_state(held_position) in active_states):
                held_positions.append(held_position)

        return tuple(held_positions)


class MembraneGroupAdapter(grok.Adapter, MembraneGroup):
    grok.context(IMembraneGroup)
    grok.implements(IGroup)


class GroupMembraneUserGroups(grok.Adapter):

    grok.context(IMembraneGroup)
    grok.implements(IMembraneUserGroups)

    def getGroupsForPrincipal(self, principal, request=None):
        group = queryAdapter(self.context.getParentNode(), IGroup)
        if group is not None:
            return (group.getGroupId(), )

        return ()
