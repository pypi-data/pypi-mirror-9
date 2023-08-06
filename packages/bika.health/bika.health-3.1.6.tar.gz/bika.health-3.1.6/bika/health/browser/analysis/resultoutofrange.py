# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from bika.lims.permissions import *
from zope.interface import implements
from zope.component import adapts


class ResultOutOfRange(object):
    """An alert provider for Analysis results outside of panic ranges
    """

    implements(IFieldIcons)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None, **kwargs):
        """ Check if result value is 'in panic'.
        """
        analysis = self.context
        path = '++resource++bika.health.images'

        translate = self.context.translate
        workflow = getToolByName(self.context, 'portal_workflow')

        astate = workflow.getInfoFor(analysis, 'review_state')
        if astate == 'retracted':
            return {}

        result = result is not None and str(result) or analysis.getResult()
        if result == '':
            return {}
        # if analysis result is not a number, then we assume in range
        try:
            result = float(str(result))
        except ValueError:
            return {}
        # No specs available, assume in range
        specs = hasattr(analysis, 'getAnalysisSpecs') \
                and analysis.getAnalysisSpecs(specification) or None
        spec_min = None
        spec_max = None
        if specs is None:
            return {}

        keyword = analysis.getService().getKeyword()
        spec = specs.getResultsRangeDict()
        if keyword in spec:
            try:
                spec_min = float(spec[keyword]['minpanic'])
            except:
                spec_min = None
                pass

            try:
                spec_max = float(spec[keyword]['maxpanic'])
            except:
                spec_max = None
                pass

            if (not spec_min and not spec_max):
                # No min and max values defined
                outofrange, acceptable, o_spec = False, None, None

            elif spec_min and spec_max and spec_min <= result <= spec_max:
                # min and max values defined
                outofrange, acceptable, o_spec = False, None, None

            elif spec_min and not spec_max and spec_min <= result:
                # max value not defined
                outofrange, acceptable, o_spec = False, None, None

            elif not spec_min and spec_max and spec_max >= result:
                # min value not defined
                outofrange, acceptable, o_spec = False, None, None

            else:
                outofrange, acceptable, o_spec = True, False, spec[keyword]

        else:
            # Analysis without specification values. Assume in range
            outofrange, acceptable, o_spec = False, None, None

        alerts = {}
        if outofrange:
            range_str = "{0} {1}, {2} {3}".format(
                translate(_("minpanic")), str(o_spec['minpanic']),
                translate(_("maxpanic")), str(o_spec['maxpanic'])
            )

            if acceptable:
                message = "{0} ({1})".format(
                    translate(_('Result in shoulder panic range')), range_str)
            else:
                message = "{0} ({1})".format(
                    translate(_('Result exceeded panic level')), range_str)

            alerts[analysis.UID()] = [{
                'msg': message,
                'icon': path + '/lifethreat.png',
                'field': 'Result', }, ]
        return alerts
