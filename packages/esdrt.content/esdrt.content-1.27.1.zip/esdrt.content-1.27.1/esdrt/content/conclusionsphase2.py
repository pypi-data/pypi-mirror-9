from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition.interfaces import IAcquirer
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from esdrt.content import MessageFactory as _
from esdrt.content.observation import hidden
from five import grok
from plone import api
from plone.app.dexterity.behaviors.discussion import IAllowDiscussion
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from time import time
from types import IntType
from z3c.form import field
from zope import schema
from zope.browsermenu.menu import getMenu
from zope.component import createObject
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import Invalid
from zope.schema.interfaces import IVocabularyFactory


class ITableRowSchema(form.Schema):

    line_title = schema.TextLine(title=_(u'Title'), required=True)
    co2 = schema.Int(title=_(u'CO\u2082'), required=False)
    ch4 = schema.Int(title=_(u'CH\u2084'), required=False)
    n2o = schema.Int(title=_(u'N\u2082O'), required=False)
    nox = schema.Int(title=_(u'NO\u2093'), required=False)
    co = schema.Int(title=_(u'CO'), required=False)
    nmvoc = schema.Int(title=_(u'NMVOC'), required=False)
    so2 = schema.Int(title=_(u'SO\u2082'), required=False)


class IConclusionsPhase2(form.Schema, IImageScaleTraversable):
    """
    Conclusions of the Second Phase of the Review
    """

    closing_reason = schema.Choice(
        title=_(u'Conclusion'),
        vocabulary='esdrt.content.conclusionphase2reasons',
        required=True,

    )

    text = schema.Text(
        title=_(u'Text'),
        required=True,
    )

    form.widget(ghg_estimations=DataGridFieldFactory)
    ghg_estimations = schema.List(
        title=_(u'GHG estimates [Gg CO2 eq.]'),
        value_type=DictRow(title=u"tablerow", schema=ITableRowSchema),
        default=[
            {'line_title': 'Original estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Technical correction proposed by  TERT', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Revised estimate by MS', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Corrected estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},

        ],
    )


@form.validator(field=IConclusionsPhase2['ghg_estimations'])
def check_ghg_estimations(value):
    for item in value:
        for val in item.values():
            if type(val) is IntType and val < 0:
                raise Invalid(u'Estimation values must be positive numbers')


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class ConclusionsPhase2(dexterity.Container):
    grok.implements(IConclusionsPhase2)

    def reason_value(self):
        return self._vocabulary_value(
            'esdrt.content.conclusionphase2reasons',
            self.closing_reason
        )

    def _vocabulary_value(self, vocabulary, term):
        vocab_factory = getUtility(IVocabularyFactory, name=vocabulary)
        vocabulary = vocab_factory(self)
        try:
            value = vocabulary.getTerm(term)
            return value.title
        except LookupError:
            return u''

    def can_edit(self):
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', self)

    def can_delete(self):
        sm = getSecurityManager()
        return sm.checkPermission('Delete objects', self)

    def can_add_files(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add ESDRTFile', self)

    def get_actions(self):
        parent = aq_parent(self)
        request = getRequest()
        question_menu_items = getMenu(
            'plone_contentmenu_workflow',
            self,
            request
        )
        observation_menu_items = getMenu(
            'plone_contentmenu_workflow',
            parent,
            request
        )
        menu_items = question_menu_items + observation_menu_items
        return [mitem for mitem in menu_items if not hidden(mitem)]

    def get_files(self):
        items = self.values()
        mtool = api.portal.get_tool('portal_membership')
        return [item for item in items if mtool.checkPermission('View', item)]


class AddForm(dexterity.AddForm):
    grok.name('esdrt.content.conclusionsphase2')
    grok.context(IConclusionsPhase2)
    grok.require('esdrt.content.AddConclusionsPhase2')

    label = 'Conclusions Step 2'
    description = ''

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = field.Fields(IConclusionsPhase2).select('closing_reason', 'text')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        self.widgets['text'].rows = 15

    def create(self, data={}):
        # import pdb; pdb.set_trace()
        # return super(AddForm, self).create(data)
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        container = aq_inner(self.context)
        content = createObject(fti.factory)
        if hasattr(content, '_setPortalTypeName'):
            content._setPortalTypeName(fti.getId())

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        if IAcquirer.providedBy(content):
            content = content.__of__(container)
        id = str(int(time()))
        content.title = id
        content.id = id
        content.text = self.request.form.get('form.widgets.text', '')
        reason = self.request.form.get('form.widgets.closing_reason')
        content.closing_reason = reason[0]
        adapted = IAllowDiscussion(content)
        adapted.allow_discussion = True
        return aq_base(content)

    def updateActions(self):
        super(AddForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class ConclusionsPhase2View(grok.View):
    grok.context(IConclusionsPhase2)
    grok.require('zope2.View')
    grok.name('view')

    def render(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        url = '%s#tab-conclusions-phase2' % parent.absolute_url()

        return self.request.response.redirect(url)


class EditForm(dexterity.EditForm):
    grok.name('edit')
    grok.context(IConclusionsPhase2)
    grok.require('cmf.ModifyPortalContent')

    label = 'Conclusions Step 2'
    description = ''

    def updateFields(self):
        super(EditForm, self).updateFields()
        self.fields = field.Fields(IConclusionsPhase2).select('closing_reason', 'text', 'ghg_estimations')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']
        self.fields['ghg_estimations'].widgetFactory = DataGridFieldFactory
        self.fields['text'].rows = 15

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['text'].rows = 15

    def updateActions(self):
        super(EditForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')