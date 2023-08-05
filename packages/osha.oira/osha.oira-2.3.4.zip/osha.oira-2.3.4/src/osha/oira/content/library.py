import collections
import logging
from zExceptions import NotFound
from Acquisition import aq_base
from Acquisition import aq_inner
from five import grok
from zope.event import notify
from zope.component import getUtility
from zope.lifecycleevent import ObjectCopiedEvent
from OFS.CopySupport import CopyError
from OFS.event import ObjectClonedEvent
from z3c.appconfig.interfaces import IAppConfig
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.dexterity.interfaces import IDexterityContainer
from plonetheme.nuplone.utils import getPortal
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from euphorie.content.interfaces import IQuestionContainer
from euphorie.content.module import item_depth
from euphorie.content.risk import IRisk
from euphorie.content.sector import ISector
from euphorie.content.survey import ISurvey
from euphorie.content.surveygroup import ISurveyGroup
from euphorie.content.behaviour.uniqueid import INameFromUniqueId
from euphorie.content.behaviour.uniqueid import get_next_id
from ..interfaces import IOSHAContentSkinLayer
from .. import _


log = logging.getLogger(__name__)
grok.templatedir('templates')


def is_allowed(context, item):
    try:
        context._verifyObjectPaste(item)
    except ValueError:
        return False
    except CopyError:
        return False
    return True


def get_library(context):
    config = getUtility(IAppConfig).get('euphorie', {})
    paths = [path.lstrip('/') for path in config.get('library', '').split()]
    if not paths:
        return []
    site = getPortal(context)
    library = []
    for path in paths:
        try:
            sector = site.restrictedTraverse(path)
        except (AttributeError, KeyError):
            log.warning('Invalid library path (not found): %s' % path)
            continue
        if not ISector.providedBy(sector):
            log.warning('Invalid library path (not a sector): %s', path)
            continue
        sector_library = []
        survey_groups = [sg for sg in sector.values()
                         if ISurveyGroup.providedBy(sg) and not sg.obsolete]
        for sg in survey_groups:
            surveys = [s for s in sg.values() if ISurvey.providedBy(s)]
            if len(surveys) != 1:
                log.warning('Ignoring surveygroup due to multiple versions: %s',
                        '/'.join(sg.getPhysicalPath()))
                continue
            tree = build_survey_tree(aq_inner(context), surveys[0])
            tree['title'] = sg.title
            sector_library.append(tree)
        if sector_library:
            sector_library.sort(key=lambda s: s['title'])
            library.append({'title': sector.title,
                            'url': sector.absolute_url(),
                            'path': '/'.join(sector.getPhysicalPath()),
                            'surveys': sector_library})
    library.sort(key=lambda s: s['title'])
    return library


def build_survey_tree(context, root):
    """Build a simple datastructure describing (part of) a survey.

    This implementation does a walk over the content itself. It is possible
    to also do this based on a catalog query, but since we use light-weight
    content items this should be simpler and removes the need to turn a
    catalog result back into a tree.
    """
    normalize = getUtility(IIDNormalizer).normalize
    tree = {'title': root.title,
            'path': '/'.join(root.getPhysicalPath()),
            'portal_type': normalize(root.portal_type),
            'children': [],
            'url': root.absolute_url(),
            }
    todo = collections.deque([(root, [], tree['children'])])
    while todo:
        (node, index, child_list) = todo.popleft()
        for (ix, child) in enumerate(node.values(), 1):
            if not (IQuestionContainer.providedBy(child) or IRisk.providedBy(child)):
                continue
            child_index = index + [str(ix)]
            info = {'title': child.title,
                    'children': [],
                    'number': '.'.join(child_index),
                    'path': '/'.join(child.getPhysicalPath()),
                    'url': child.absolute_url(),
                    'disabled': not is_allowed(context, child),
                    'portal_type': normalize(child.portal_type),
                    }
            child_list.append(info)
            todo.append((child, child_index, info['children']))
    return tree


class Library(grok.View):
    grok.context(IQuestionContainer)
    grok.layer(IOSHAContentSkinLayer)
    grok.require('euphorie.content.AddNewRIEContent')
    grok.template('library')

    def update(self):
        self.library = get_library(self.context)
        if not self.library:
            raise NotFound(self, 'library', self.request)
        self.depth = item_depth(aq_inner(self.context))
        self.at_root = not self.depth
        super(Library, self).update()


def assign_ids(context, tree):
    uid_handler = getToolByName(context, 'portal_uidhandler')
    todo = collections.deque([(None, tree)])
    while todo:
        (parent, item) = todo.popleft()
        uid_handler.register(item)
        if INameFromUniqueId.providedBy(item):
            old_id = item.id
            new_id = get_next_id(context)
            item._setId(new_id)
            if parent is not None:
                # We need to reset the child in its folder to make sure
                # the folder knows of the new id.
                position = parent.getObjectPosition(old_id)
                del parent[old_id]
                parent._setObject(new_id, item, suppress_events=True)
                parent.moveObjectToPosition(new_id, position, True)
        if IDexterityContainer.providedBy(item):
            for gc in item.values():
                todo.append((item, aq_base(gc)))


class LibraryInsert(grok.View):
    grok.name('library-insert')
    grok.context(IQuestionContainer)
    grok.layer(IOSHAContentSkinLayer)
    grok.require('euphorie.content.AddNewRIEContent')

    def render(self):
        if self.request.method != 'POST':
            raise NotFound(self, 'library-insert', self.request)
        path = self.request.form.get('path')
        if not path:
            raise NotFound(self, 'library-insert', self.request)  # XXX Wrong exception type
        target = aq_inner(self.context)
        app = target.getPhysicalRoot()
        source = app.restrictedTraverse(path)
        if not is_allowed(target, source):
            raise NotFound(self, 'library-insert', self.request)  # XXX Wrong exception type
        copy = source._getCopy(target)
        assign_ids(target, copy)
        notify(ObjectCopiedEvent(copy, source))
        target._setObject(copy.id, copy)
        copy = target[copy.id]
        copy._postCopy(target, op=0)
        notify(ObjectClonedEvent(copy))

        IStatusMessage(self.request).addStatusMessage(
                _(u'Addded a copy of "${title}" to your survey.',
                    mapping={'title': copy.title}),
                type='success')
        self.response.redirect(copy.absolute_url())
