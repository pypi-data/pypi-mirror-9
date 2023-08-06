""" Control Panel
"""
from zope.component import queryUtility
from zope.interface import implements
from zope.formlib import form
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from plone.registry.interfaces import IRegistry
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from eea.annotator.interfaces import ISettings
from eea.annotator.config import EEAMessageFactory as _

class ControlPanel(ControlPanelForm):
    """ API
    """
    form_fields = form.FormFields(ISettings)
    form_fields['portalTypes'].custom_widget = MultiCheckBoxVocabularyWidget

    label = _(u"EEA Annotator Settings")
    description = _(u"EEA Annotator settings")
    form_name = _(u"EEA Annotator settings")

class ControlPanelAdapter(SchemaAdapterBase):
    """ Form adapter
    """
    implements(ISettings)

    def __init__(self, context):
        super(ControlPanelAdapter, self).__init__(context)
        self._settings = None

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            self._settings = queryUtility(
                IRegistry).forInterface(ISettings, False)
        return self._settings

    @property
    def portalTypes(self):
        """ Get portalTypes
        """
        name = u"portalTypes"
        return getattr(self.settings, name, ISettings[name].default)

    @portalTypes.setter
    def portalTypes(self, value):
        """ Set portalTypes
        """
        self.settings.portalTypes = value

    @property
    def autoSync(self):
        """ Auto refresh inline comments interval
        """
        name = u"autoSync"
        return getattr(self.settings, name, ISettings[name].default)

    @autoSync.setter
    def autoSync(self, value):
        """ Set Auto refresh inline comments interval
        """
        self.settings.autoSync = value

    def disabled(self, obj):
        """ Check if inline comments are disabled for obj
        """
        ctype = getattr(obj, 'portal_type', '')
        if ctype not in self.portalTypes:
            return True
        return False

    @property
    def minWords(self):
        """ Minimum number of words to comment on
        """
        name = u"minWords"
        return getattr(self.settings, name, ISettings[name].default)

    @minWords.setter
    def minWords(self, value):
        """ Set Minimum number of words to comment on
        """
        self.settings.minWords = value

    @property
    def noDuplicates(self):
        """ Don't allow duplicates
        """
        name = u"noDuplicates"
        return getattr(self.settings, name, ISettings[name].default)

    @noDuplicates.setter
    def noDuplicates(self, value):
        """ Set whether or not to allow duplicates
        """
        self.settings.noDuplicates = value
