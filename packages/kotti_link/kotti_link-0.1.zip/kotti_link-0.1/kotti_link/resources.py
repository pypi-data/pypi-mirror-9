from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode

from kotti.resources import Document

from kotti_link import _


class Link(Document):
    """Link content type"""

    id = Column(
        Integer(),
        ForeignKey('documents.id'),
        primary_key=True
    )
    link = Column(Unicode(230))

    type_info = Document.type_info.copy(
        name=u'Link',
        title=_(u'Link'),
        add_view=u'add_link',
        addable_to=['Document', ],
        selectable_default_views=[
            ('redirect', _(u"Redirect View")),
            ('popup', _(u"Popup View")),
        ],
    )

    def __init__(self, link=u'', **kwargs):
        super(Link, self).__init__(**kwargs)
        self.link = link
