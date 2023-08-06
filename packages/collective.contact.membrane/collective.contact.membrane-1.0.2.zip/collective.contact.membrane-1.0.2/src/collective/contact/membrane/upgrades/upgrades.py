# -*- coding: utf-8 -*-
"""Upgrades for collective.contact.membrane."""
#pylint: disable=E1121

from ecreall.helpers.upgrade.interfaces import IUpgradeTool


def v2(context):
    """Upgrade to v2."""
    tool = IUpgradeTool(context)


def v3(context):
    """Upgrade to v3."""
    tool = IUpgradeTool(context)
    tool.runImportStep('collective.contact.membrane', 'plone.app.registry')
