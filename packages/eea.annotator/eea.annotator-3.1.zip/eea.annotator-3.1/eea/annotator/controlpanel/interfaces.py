""" Control Panel Interfaces

   >>> portal = layer['portal']
   >>> sandbox = portal['sandbox']

"""
from zope.interface import Interface
from zope import schema
from eea.annotator.config import EEAMessageFactory as _

class ISettings(Interface):
    """ Settings

        >>> from eea.annotator.interfaces import ISettings
        >>> ISettings(portal).portalTypes = [u'Document', u'News Item']
        >>> ISettings(portal).portalTypes
        [u'Document', u'News Item']

    """
    portalTypes = schema.List(
        title=_(u"Enable inline comments"),
        description=_(u"Annotator inline comments are enabled for the "
                      u"following content-types"),
        required=False,
        default=[u"Document"],
        value_type=schema.Choice(
            vocabulary=u"plone.app.vocabularies.ReallyUserFriendlyTypes")
    )

    autoSync = schema.Int(
        title=_(u"Auto-refresh inline comments"),
        description=_(
            u"Define the auto-refresh interval in seconds of inline comments "
            u"within a page. Minimum recommended 30 seconds. "
            u"Use 0 to disable auto-refresh."
        ),
        required=False,
        default=0
    )

    minWords = schema.Int(
        title=_(u"Minimum number of words"),
        description=_(u"Force user to select at least this number of words "
                      u"while adding an inline comment"
        ),
        required=False,
        default=0
    )

    noDuplicates = schema.Bool(
        title=_(u"Do not allow duplicates"),
        description=_(u"If the user selects a text that is also found "
                      u"elsewhere in the same page display a warning message "
                      u"and restrict addition on inline comment"),
        required=False,
        default=False
    )
