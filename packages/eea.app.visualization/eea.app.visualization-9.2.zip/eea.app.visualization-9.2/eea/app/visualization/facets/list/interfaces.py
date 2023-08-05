""" Interfaces
"""
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from eea.app.visualization.facets.interfaces import IVisualizationEditFacet
from eea.app.visualization.config import EEAMessageFactory as _

class IListProperties(IVisualizationEditFacet):
    """ Edit numeric facet
    """
    ex_height = schema.TextLine(
        title=_(u"Height"),
        description=_(u"height of the facet's body, e.g., '20em', '200px'"),
        required=False,
        default=u""
    )

    ex_sortMode = schema.Choice(
        title=_(u"Sort mode"),
        description=_(u"how to sort the choices in the facet"),
        required=False,
        default=u"value",
        vocabulary=SimpleVocabulary([
            SimpleTerm(u"value", u"value", u"Value"),
            SimpleTerm(u"count", u"count", u"Count"),
        ])
    )

    ex_sortDirection = schema.Choice(
            title=_(u"Sort direction"),
            description=_(u"whether to reverse the sort direction"),
            required=False,
            default=u"forward",
            vocabulary=SimpleVocabulary([
                SimpleTerm(u"forward", u"forward", u"Forward"),
                SimpleTerm(u"reverse", u"reverse", u"Reverse"),
            ])
        )

    ex_showMissing = schema.Bool(
        title=_(u"Show missing"),
        description=_(u"whether to provide a selection for items missing "
                      "the facet -- this will suppress the "
                      "'(missing this field)' text"),
        required=False,
        default=True
    )

    ex_missingLabel = schema.TextLine(
        title=_(u"Missing label"),
        description=_(u"missing label"),
        required=False,
        default=u""
    )

    ex_selection = schema.TextLine(
        title=_(u"Selection"),
        description=_(u"semicolon-separated list of default selections"),
        required=False,
        default=u""
    )

    ex_fixedOrder = schema.TextLine(
        title=_(u"Fixed Order"),
        description=_(u"semicolon-separated list of values specifying a "
                      "fixed order for sorting the choices in the facet, "
                      "e.g., 'Mo;Tu;We;Th;Fr' for weekdays"),
        required=False,
        default=u""
    )

    ex_scroll = schema.Bool(
        title=_(u"Scroll"),
        description=_(u"if true, facet values are in a scrollable window "
                      "of fixed size. If false, all facet values are shown "
                      "in as much space as needed, without a scroll bar."),
        required=False,
        default=True
    )

    ex_collapsible = schema.Bool(
        title=_(u"Collapsible"),
        description=_(u"collapsible"),
        required=False,
        default=False
    )

    ex_collapsed = schema.Bool(
        title=_(u"Collapsed"),
        description=_(u"collapsed"),
        required=False,
        default=False
    )

    ex_colorCoder = schema.TextLine(
        title=_(u"Color coder"),
        description=_(u"color coder"),
        required=False,
        default=u""
    )

    ex_formatter = schema.TextLine(
        title=_(u"Formatter"),
        description=_(u"formatter"),
        required=False,
        default=u""
    )
