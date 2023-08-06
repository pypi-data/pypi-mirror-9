""" Custom traverse
"""
import logging
from zope.interface import Interface
from zope.component import queryMultiAdapter
from zope.component import adapts
from eea.annotator.interfaces import ILayer

from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.imaging.interfaces import IBaseObject

logger = logging.getLogger('eea.annotator')

try:
    from eea.depiction import traverse
    ScaleTraverser = traverse.ScaleTraverser
except (ImportError, AttributeError), err:
    logger.debug(err)
    from plone.app.imaging.traverse import ImageTraverser as ScaleTraverser

try:
    from plone.dexterity import interfaces
    IDexterityContent = interfaces.IDexterityContent
    from plone.dexterity.browser import traversal
    DexterityPublishTraverse = traversal.DexterityPublishTraverse
except (ImportError, AttributeError), err:
    logger.debug(err)
    DexterityPublishTraverse = ScaleTraverser
    class IDexterityContent(Interface):
        """ Fallback
        """

from eea.annotator.interfaces import IAnnotatorAware
from eea.annotator.browser.interfaces import IAnnotatorAPI
#
# IAnnotatorAware Archetypes
#
class AnnotatorAwareTraverse(ScaleTraverser):
    """Override the default browser publisher to make WebDAV work for
    Annotator aware objects.
    """
    adapts(IBaseObject, ILayer)

    def publishTraverse(self, request, name):
        """ Custom traverser
        """
        if IAnnotatorAware.providedBy(self.context):
            if name == 'annotator.api':
                if request.method in ('PUT', 'DELETE'):
                    return queryMultiAdapter((self.context, self.request),
                                             name=u'annotator.api')

        return super(AnnotatorAwareTraverse,
                                 self).publishTraverse(request, name)
#
# IAnnotatorAware Dexterity
#
class DexterityAnnotatorAwareTraverse(DexterityPublishTraverse):
    """ Handle annotator.api by dexterity ctyoes
    """
    adapts(IDexterityContent, ILayer)

    def publishTraverse(self, request, name):
        """ Custom traverser
        """
        if IAnnotatorAware.providedBy(self.context):
            if name == 'annotator.api':
                if request.method in ('PUT', 'DELETE'):
                    return queryMultiAdapter((self.context, self.request),
                                             name=u'annotator.api')

        return super(DexterityAnnotatorAwareTraverse,
                                 self).publishTraverse(request, name)
#
# IAnnotatorAPI
#
class AnnotatorAPITraverse(DefaultPublishTraverse):
    """Override the default browser publisher to make WebDAV work for
    Annotator aware objects.
    """

    adapts(IAnnotatorAPI, ILayer)

    def publishTraverse(self, request, name):
        """ Custom traverser
        """
        if name.startswith('annotations') and getattr(
            request, 'maybe_webdav_client', False):
            if request.method in ('PUT', 'DELETE'):
                return queryMultiAdapter(
                    (self.context, self.request), name=name)

        return super(AnnotatorAPITraverse, self).publishTraverse(request, name)
