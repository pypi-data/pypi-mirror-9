""" Portlets
"""
from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.security import checkPermission
from zope.component.hooks import getSite
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from eea.annotator.interfaces import IAnnotatorStorage
from eea.annotator.controlpanel.interfaces import ISettings
from eea.annotator.config import EEAMessageFactory as _

class IAnnotatorPortlet(IPortletDataProvider):
    """ Annotator portlet
    """
    label = schema.TextLine(
        title=_(u"Porlet title"),
        description=_(u"Title of the portlet. Leave empty if you don't want "
                      u"to display a title for this portlet"),
        default=u"Inline comments",
        required=False
    )

class Assignment(base.Assignment):
    """ Assignment
    """
    implements(IAnnotatorPortlet)

    def __init__(self, label=u"Inline comments"):
        self.label = label

    @property
    def title(self):
        """ Get portlet title
        """
        return self.label or u'Inline comments'

class AddForm(base.AddForm):
    """ Add portlet
    """
    form_fields = form.Fields(IAnnotatorPortlet)
    label = _(u"Add Inline comments (Annotator) portlet")
    description = _(
        u"This portlet traces all inline comments for this document")

    @property
    def schema(self):
        """ z3c.form schema
        """
        return IAnnotatorPortlet

    def create(self, data):
        """ Create
        """
        return Assignment(label=data.get('label', u'Inline comments'))

class EditForm(base.EditForm):
    """ Portlet edit
    """
    form_fields = form.Fields(IAnnotatorPortlet)
    label = _(u"Edit Inline comments (Annotator) portlet")
    description = _(
        u"This portlet traces all inline comments for this document")

class Renderer(base.Renderer):
    """ portlet renderer
    """
    render = ViewPageTemplateFile('annotator.pt')

    @property
    def user(self):
        """ Current user
        """
        if not getattr(self, '_user', None):
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            self._user = member.getId()
        return self._user

    @property
    def moderate(self):
        """ Can moderate inline comments
        """
        if not checkPermission('eea.annotator.manage', self.context):
            return False
        return True

    @property
    def can_subscribe(self):
        """ Is current user subscribed
        """
        if not checkPermission('eea.annotator.view', self.context):
            return False

        storage = queryAdapter(self.context, IAnnotatorStorage)
        if not storage:
            return False

        subscribed = storage.subscribers.get(self.user, False)
        if not subscribed:
            return True
        return False

    @property
    def can_unsubscribe(self):
        """ Is current user subscribed
        """
        if not checkPermission('eea.annotator.view', self.context):
            return False

        storage = queryAdapter(self.context, IAnnotatorStorage)
        if not storage:
            return False

        if self.can_subscribe:
            return False
        return True

    @property
    def available(self):
        """By default, portlets are available on view view and edit view
        """

        if not checkPermission('eea.annotator.view', self.context):
            return False

        plone = getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')
        is_edit_view = 'edit' in self.request.URL0.split('/')[-1]
        if not (plone.is_view_template() or is_edit_view):
            return False

        storage = queryAdapter(self.context, IAnnotatorStorage)
        if storage and storage.disabled:
            return False

        site = getSite()
        settings = queryAdapter(site, ISettings)
        if settings.disabled(self.context):
            return False

        return True
