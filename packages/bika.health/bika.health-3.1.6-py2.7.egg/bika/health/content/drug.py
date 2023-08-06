from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.health.config import PROJECTNAME
from bika.lims.browser.widgets import RecordsWidget
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    StringField('Category',
        widget = StringWidget(
            label = _("Category"),
        )
    ),

    TextField('Indications',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Drug indications",
                      "Indications"),
            description = _("Symptoms or the like for which the drug is suitable"),
        ),
    ),

    TextField('Posology',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Drug posology",
                      "Posology"),
            description = _("Appropriate doses and dosage"),
        ),
    ),

    TextField('SideEffects',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Drug side effects",
                      "Side effects"),
            description = _("Known undesirable effects of the drug"),
        ),
    ),

    TextField('Preservation',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Drug preservation",
                      "Preservation"),
            description = _("preservation"),
        ),
    ),

))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Drug(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Drug, PROJECTNAME)
