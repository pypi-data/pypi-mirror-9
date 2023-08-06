""" Add facets
"""
from zope.component import queryAdapter
from zope.formlib.form import SubPageForm
from zope.formlib.form import action as formAction
from zope.formlib.form import setUpInputWidgets, haveInputWidgets
from eea.app.visualization.interfaces import IVisualizationConfig
from eea.app.visualization.zopera import IStatusMessage
from zope.formlib.form import Fields

from eea.app.visualization.facets.interfaces import IVisualizationAddFacet

from eea.app.visualization.config import EEAMessageFactory as _

class AddForm(SubPageForm):
    """
    Basic layer to add daviz facets. For more details on how to use this,
    see implementation in eea.app.visualization.facets.list.add.Add.

    Assign these attributes in your subclass:
      - form_fields: Fields(Interface)

    """
    form_fields = Fields(IVisualizationAddFacet)
    _prefix = 'form'
    _action = ''

    def __init__(self, context, request):
        super(AddForm, self).__init__(context, request)
        for key in self.request.form:
            if key.endswith('.label'):
                self._prefix = key.split('.')[0]
                break

    def getPrefix(self):
        """ Form prefix getter
        """
        return self._prefix

    def setPrefix(self, value):
        """ Form prefix setter
        """
        self._prefix = value

    prefix = property(getPrefix, setPrefix)

    def setUpWidgets(self, ignore_request=False):
        """ Setup widgets
        """
        self.widgets = setUpInputWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request,
            )

    @formAction(_("Add"), condition=haveInputWidgets)
    def handle_add(self, action, data):
        """ Handle add
        """
        self._action = action.__name__
        self.createAndAdd(data)

    def createAndAdd(self, data):
        """ Create and Add
        """
        ob = self.create(data)
        return self.add(ob)

    def create(self, data):
        """ Create
        """
        return data

    _finished_add = False

    def add(self, obj):
        """ Add
        """
        mutator = queryAdapter(self.context, IVisualizationConfig)
        mutator.add_facet(**obj)
        self._finished_add = True
        return obj

    def render(self):
        """ Render
        """
        if self._finished_add:
            ajax = (self.request.form.get(self._action, '') == 'ajax')
            if ajax:
                return _('Facet added')
            self.request.response.redirect(self.nextURL())
            return ""

        return super(AddForm, self).render()

    def nextURL(self):
        """ Next
        """
        status = queryAdapter(self.request, IStatusMessage)
        if status:
            status.addStatusMessage(_('Facet added'), type='info')
        nexturl = self.context.absolute_url() + '/daviz-edit.html'
        self.request.response.redirect(nexturl)
