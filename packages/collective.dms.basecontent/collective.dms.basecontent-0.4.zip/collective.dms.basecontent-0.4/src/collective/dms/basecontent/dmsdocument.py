from zope import schema
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy

from plone.supermodel import model
from collective.dms.basecontent.relateddocs import RelatedDocs
from collective.z3cform.rolefield.field import LocalRolesToPrincipals

from . import _
from .widget import AjaxChosenMultiFieldWidget

class IDmsDocument(model.Schema):
    """Schema for DmsDocument"""

    notes = schema.Text(
        title=_(u"Notes"),
        required=False,
    )

    treating_groups = LocalRolesToPrincipals(
        title=_(u"Treating groups"),
        required=False,
        roles_to_assign=('Editor',),
        value_type=schema.Choice(vocabulary=u'collective.dms.basecontent.treating_groups',)
    )
    form.widget(treating_groups=AjaxChosenMultiFieldWidget)

    recipient_groups = LocalRolesToPrincipals(
        title=_(u"Recipient groups"),
        required=False,
        roles_to_assign=('Reader',),
        value_type=schema.Choice(vocabulary=u'collective.dms.basecontent.recipient_groups')
    )
    form.widget(recipient_groups=AjaxChosenMultiFieldWidget)

    related_docs = RelatedDocs(
        title=_(u"Related documents"),
        required=False,
        display_backrefs=True,
    )


class DmsDocument(Container):
    """DmsDocument"""
    implements(IDmsDocument)
    # disable local roles inheritance
    __ac_local_roles_block__ = True

    treating_groups = FieldProperty(IDmsDocument['treating_groups'])
    recipient_groups = FieldProperty(IDmsDocument['recipient_groups'])


class DmsDocumentSchemaPolicy(DexteritySchemaPolicy):
    """DmsDocument schema policy"""

    def bases(self, schemaName, tree):
        return (IDmsDocument, )
