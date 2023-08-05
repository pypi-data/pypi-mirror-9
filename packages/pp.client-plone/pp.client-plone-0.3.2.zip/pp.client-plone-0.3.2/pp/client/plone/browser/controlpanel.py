# -*- coding: utf-8 -*-

################################################################
# pp.client-plone
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################


from plone.app.registry.browser import controlpanel

from pp.client.plone.interfaces import IPPClientPloneSettings
from pp.client.plone.i18n import MessageFactory as _


class PPClientPloneSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IPPClientPloneSettings
    label = _(u'PP Client Plone settings')
    description = _(u'')

    def updateFields(self):
        super(PPClientPloneSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(PPClientPloneSettingsEditForm, self).updateWidgets()


class PPClientPloneSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = PPClientPloneSettingsEditForm
