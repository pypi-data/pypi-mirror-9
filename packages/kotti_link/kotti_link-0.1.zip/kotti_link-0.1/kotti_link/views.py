# -*- coding: utf-8 -*-

from colander import SchemaNode
from colander import String
from kotti.views.edit.content import DocumentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound

from kotti.security import has_permission

from kotti_link import _
from kotti_link.resources import Link
from kotti_link.fanstatic import kotti_link


class LinkSchema(DocumentSchema):
    """Schema for add / edit forms of Link"""

    link = SchemaNode(
        String(),
        title=_(u'Link'),
    )


@view_config(name=Link.type_info.add_view,
             permission='add',
             renderer='kotti:templates/edit/node.pt')
class LinkAddForm(AddFormView):

    schema_factory = LinkSchema
    add = Link
    item_type = _(u"Link")


@view_config(name='edit',
             context=Link,
             permission='edit',
             renderer='kotti:templates/edit/node.pt')
class LinkEditForm(EditFormView):

    schema_factory = LinkSchema


@view_defaults(context=Link)
class LinkView(object):
    """View(s) for Link"""

    def __init__(self, context, request):

        self.context = context
        self.request = request

    @view_config(name='view',
                 renderer='kotti:templates/view/document.pt')
    def view(self):
        return {}

    @view_config(name='redirect',
                 renderer='kotti_link:templates/redirect.pt')
    def redirect(self):
        """View that redirects the user to the given link. If the user
           has the edit permission a template with a hint is presented.
        """
        if has_permission(u'edit', self.context, self.request):
            kotti_link.need()
            return {}

        return HTTPFound(location=self.context.link)

    @view_config(name='popup',
                 renderer='kotti_link:templates/popup.pt')
    def popup(self):
        """View that present the target of the given link in a popup.
        """
        kotti_link.need()
        return {}
