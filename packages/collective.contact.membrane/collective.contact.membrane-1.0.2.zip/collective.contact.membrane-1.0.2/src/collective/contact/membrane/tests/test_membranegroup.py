# -*- coding: utf8 -*-
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue

from plone import api

from ecreall.helpers.testing.base import BaseTest

from collective.contact.membrane.behaviors.membranegroup import MembraneGroupAdapter
from collective.contact.membrane.behaviors.personmembraneuser import PersonMembraneUserGroups

from ..testing import IntegrationTestCase


class TestMembraneGroup(IntegrationTestCase, BaseTest):
    """Tests that organization and position content types are membrane groups
    """

    def setUp(self):
        super(TestMembraneGroup, self).setUp()
        portal = api.portal.get()
        self.armeedeterre = portal.mydirectory.armeedeterre
        self.general_adt = self.armeedeterre.general_adt
        self.brigadelh = self.armeedeterre.corpsa.divisionalpha.regimenth.brigadelh
        self.sergent_lh = self.armeedeterre.corpsa.divisionalpha.regimenth.brigadelh.sergent_lh
        self.dummyperson = api.content.create(type='person', id='dummyperson',
                                              container=portal.mydirectory)
        membrane_tool = api.portal.get_tool('membrane_tool')
        membrane_tool.reindexObject(self.dummyperson)
        membrane_tool.reindexObject(self.armeedeterre)
        membrane_tool.reindexObject(self.general_adt)
        membrane_tool.reindexObject(self.brigadelh)
        membrane_tool.reindexObject(self.sergent_lh)

    def test_get_organization_group(self):
        armeedeterre_group = api.group.get(groupname='armeedeterre')
        self.assertTrue(armeedeterre_group.isGroup())
        self.assertEqual(len(armeedeterre_group.getGroupMembers()), 1)

    def test_get_position_group(self):
        general_adt_group = api.group.get(groupname='armeedeterre_general_adt')
        self.assertTrue(general_adt_group.isGroup())
        self.assertEqual(len(general_adt_group.getGroupMembers()), 1)

    def test_get_organization_group_members(self):
        armeedeterre = self.armeedeterre
        dummyperson = self.dummyperson
        adapter = MembraneGroupAdapter(armeedeterre)
        self.assertEqual(len(adapter.getGroupMembers()), 1)
        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(armeedeterre))
        api.content.create(container=dummyperson, type='held_position',
                           id='dummyperson_adt', position=relation)
        self.assertEqual(len(adapter.getGroupMembers()), 2)
        self.assertIn(dummyperson.UID(), adapter.getGroupMembers())

    def test_get_position_group_members(self):
        general_adt = self.general_adt
        dummyperson = self.dummyperson
        adapter = MembraneGroupAdapter(general_adt)
        self.assertEqual(len(adapter.getGroupMembers()), 1)
        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(general_adt))
        api.content.create(container=dummyperson, type='held_position',
                           id='dummyperson_gadt', position=relation)
        self.assertEqual(len(adapter.getGroupMembers()), 2)
        self.assertIn(dummyperson.UID(), adapter.getGroupMembers())


    def test_get_groups_for_principal(self):
        armeedeterre = self.armeedeterre
        dummyperson = self.dummyperson
        adapter = PersonMembraneUserGroups(dummyperson)
        self.assertEqual(adapter.getGroupsForPrincipal(dummyperson), ())
        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(armeedeterre))
        api.content.create(container=dummyperson, type='held_position',
                           id='dummyperson_adt', position=relation)
        self.assertEqual(adapter.getGroupsForPrincipal(dummyperson), ('armeedeterre', ))

        relation = RelationValue(intids.getId(self.sergent_lh))
        api.content.create(container=dummyperson, type='held_position',
                           id='dummyperson_sergent_lh', position=relation)
        groups = adapter.getGroupsForPrincipal(dummyperson)
        self.assertIn('armeedeterre', groups)
        self.assertIn('armeedeterre_corpsa_divisionalpha_regimenth_brigadelh_sergent_lh', groups)

        # test getGroups
        groups = api.user.get(userid=dummyperson.UID()).getGroups()
        self.assertIn('armeedeterre', groups)
        self.assertIn('armeedeterre_corpsa_divisionalpha_regimenth_brigadelh_sergent_lh', groups)
        self.assertIn('armeedeterre_corpsa_divisionalpha_regimenth_brigadelh_sergent_lh', groups)
        self.assertIn('armeedeterre_corpsa', groups)
        self.assertIn('armeedeterre', groups)

        sergent_lh_group = api.group.get(groupname='armeedeterre_corpsa_divisionalpha_regimenth_brigadelh_sergent_lh')
        groups = sergent_lh_group.getGroups()
        self.assertIn('armeedeterre_corpsa_divisionalpha_regimenth_brigadelh',
                      groups)
        self.assertIn('armeedeterre_corpsa_divisionalpha_regimenth', groups)
        self.assertIn('armeedeterre_corpsa', groups)
        self.assertIn('armeedeterre', groups)
