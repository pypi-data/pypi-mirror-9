from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims import PMF as _p
from bika.lims.browser import BrowserView
from bika.lims.permissions import *


class AllergiesView(BrowserView):
    template = ViewPageTemplateFile("allergies.pt")

    def __call__(self):
        if 'submitted' in self.request:
            self.context.setAllergies(self.request.form.get('Allergies', ()))
            self.context.plone_utils.addPortalMessage(_p("Changes saved"))
        return self.template()
