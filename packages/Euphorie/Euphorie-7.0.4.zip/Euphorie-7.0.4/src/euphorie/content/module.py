import sys
from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from zope.interface import implements
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope import schema
from five import grok
from plone.directives import form
from plone.directives import dexterity
from plonetheme.nuplone.z3cform.directives import depends
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from htmllaundry.z3cform import HtmlText
from .fti import ConditionalDexterityFTI
from .fti import IConstructionFilter
from .fti import check_fti_paste_allowed
from .behaviour.uniqueid import INameFromUniqueId
from .behaviour.uniqueid import get_next_id
from .behaviour.richdescription import IRichDescription
from .interfaces import IQuestionContainer
from .. import MessageFactory as _
from .risk import IRisk
from .utils import StripMarkup
from plone.namedfile import field as filefield
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from plone.indexer import indexer

grok.templatedir("templates")


class IModule(form.Schema, IRichDescription, IBasic):
    """Survey Module.

    A module is (hierarchical) grouping in a survey.
    """
    description = HtmlText(
            title=_("label_module_description", u"Description"),
            description=_("help_module_description",
                default=u"Include any relevant information that may be "
                        u"helpful for users."),
            required=False)
    form.widget(description=WysiwygFieldWidget)
    form.order_after(description="title")

    optional = schema.Bool(
            title=_("label_module_optional",
                default=u"This module is optional"),
            description=_("help_module_optional",
                default=u"Allow users to skip this module and "
                        u"everything inside it."),
            required=False,
            default=False)

    depends("question", "optional", "on")
    question = schema.TextLine(
            title=_("label_module_question", default=u"Question"),
            description=_("help_module_question",
                default=u"The question to ask users if this module is "
                        u"optional. This has to be a yes/no question."),
            required=False)

    image = filefield.NamedBlobImage(
            title=_("label_image", default=u"Image file"),
            description=_("help_image_upload",
                default=u"Upload an image. Make sure your image is of format "
                        u"png, jpg or gif and does not contain any special "
                        u"characters."),
            required=False)
    caption = schema.TextLine(
            title=_("label_caption", default=u"Image caption"),
            required=False)

    solution_direction = HtmlText(
            title=_("label_solution_direction",
                default=u"Introduction action plan"),
            description=_("help_solution_direction",
                default=u"This information will be shown to users when "
                        u"they enter this module while working on the "
                        u"action plan."),
            required=False)
    form.widget(solution_direction=WysiwygFieldWidget)


class Module(dexterity.Container):
    implements(IModule, IQuestionContainer)

    image = None
    caption = None

    def _get_id(self, orig_id):
        """Pick an id for pasted content."""
        frame = sys._getframe(1)
        ob = frame.f_locals.get('ob')
        if ob is not None and INameFromUniqueId.providedBy(ob):
            return get_next_id(self)
        return super(Module, self)._get_id(orig_id)

    def _verifyObjectPaste(self, object, validate_src=True):
        super(Module, self)._verifyObjectPaste(object, validate_src)
        if validate_src:
            check_fti_paste_allowed(self, object)
            if IQuestionContainer.providedBy(object):
                my_depth = item_depth(self)
                paste_depth = tree_depth(object)
                if my_depth + paste_depth > ConstructionFilter.maxdepth:
                    raise ValueError('Pasting would create a too deep structure.')


@indexer(IModule)
def SearchableTextIndexer(obj):
    return " ".join([obj.title,
                     StripMarkup(obj.problem_description),
                     StripMarkup(obj.question),
                     StripMarkup(obj.solution_direction)])


class View(grok.View):
    grok.context(IModule)
    grok.require("zope2.View")
    grok.layer(NuPloneSkin)
    grok.template("module_view")
    grok.name("nuplone-view")

    def _morph(self, child):
        state = getMultiAdapter((child, self.request),
                name="plone_context_state")
        return {'id': child.id,
                'title': child.title,
                'url': state.view_url()}

    def update(self):
        self.modules = [self._morph(child) for child in self.context.values()
                        if IModule.providedBy(child)]
        self.risks = [self._morph(child) for child in self.context.values()
                      if IRisk.providedBy(child)]


class Edit(form.SchemaEditForm):
    """Override for the standard edit form so we can change the form title
    for submodules.
    """
    grok.context(IModule)
    grok.require("cmf.ModifyPortalContent")
    grok.layer(NuPloneSkin)
    grok.name("edit")

    @property
    def label(self):
        from euphorie.content.survey import ISurvey
        container = aq_parent(aq_inner(self.context))
        if ISurvey.providedBy(container):
            return _(u"Edit Module")
        else:
            return _(u"Edit Submodule")

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].addClass("span-7")


def tree_depth(obj):
    """Determine how deeply nested a module structure is. This is the opposite
    of item_depth.
    """
    submodules = [v for v in obj.values() if IQuestionContainer.providedBy(v)]
    if not submodules:
        return 1
    else:
        return 1 + max(tree_depth(m) for m in submodules)


def item_depth(item):
    """Return the survey depth of an item.
    """
    from euphorie.content.survey import ISurvey
    depth = 0
    for position in aq_chain(item):
        if ISurvey.providedBy(position):
            break
        depth += 1
    else:
        return None  # Not in a survey
    return depth


class ConstructionFilter(grok.MultiAdapter):
    """FTI construction filter for :py:class:`Module` objects. This filter
    does two things: it restricts the maximum depth at which a module can
    be created, and it prevents creating of modules if the current container
    already contains a risk.

    This multi adapter requires the use of the conditional FTI as implemented
    by :py:class:`euphorie.content.fti.ConditionalDexterityFTI`.
    """

    grok.adapts(ConditionalDexterityFTI, Interface)
    grok.implements(IConstructionFilter)
    grok.name("euphorie.module")

    maxdepth = 3

    def __init__(self, fti, container):
        self.fti = fti
        self.container = container

    def checkDepth(self):
        """Check if creating a new module would create a too deeply nested
        structure.
        """
        depth = item_depth(self.container)
        if depth is None:
            return True
        return (depth + 1) <= self.maxdepth

    def checkForRisks(self):
        """Check if the container already contains a risk. If so refuse to
        allow creation of a module.
        """
        for key in self.container:
            pt = self.container[key].portal_type
            if pt == "euphorie.risk":
                return False
        else:
            return True

    def allowed(self):
        return self.checkDepth() and self.checkForRisks()
