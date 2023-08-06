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

    StringField('Type',
        vocabulary = "getTreatmentTypesList",
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Treatment type",
                      "Type"),
            description = _("Select a type of treatment."),
        ),
    ),

    TextField('Procedure',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Treatment procedure",
                      "Procedure"),
        ),
    ),

    TextField('Care',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Treatment care"),
        ),
    ),

    TextField('SubjectiveClinicalFindings',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Subjective clinical findings"),
        ),
    ),

    TextField('ObjectiveClinicalFindings',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Objective clinical findings"),
        ),
    ),

    FileField('TreatmentDocument',
        widget = FileWidget(
            label = _("Treatment Document"),
        )
    ),

))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

def getTreatmentTypes(context):
    """ Return the current list of treatment types
    """
    # From Dorland's Medical Dictionary for Health Consumers. &copy 2007 by Saunders.
    types = [
             ('active', context.translate(_('Active treatment'))),
             ('causal', context.translate(_('Causal treatment'))),
             ('conservative', context.translate(_('Conservative treatment'))),
             ('empirical', context.translate(_('Empirical treatment'))),
             ('expectant', context.translate(_('Expectant/Symptomatic treatment'))),
             ('palliative', context.translate(_('Palliative treatment'))),
             ('preventive', context.translate(_('Preventive/Prophylactic treatment'))),
             ('rational', context.translate(_('Rational treatment'))),
             ('shock', context.translate(_('Shock treatment'))),
             ('specific', context.translate(_('Specific treatment'))),
             ('supporting', context.translate(_('Supporting treatment'))),
             ]
    return DisplayList(types)

class Treatment(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getTreatmentTypesList(self):
        return getTreatmentTypes(self)

registerType(Treatment, PROJECTNAME)
