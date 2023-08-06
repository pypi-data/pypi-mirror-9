import logging
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.mixins import Owned, Nested, Meta

log = logging.getLogger(__name__)


class CommentFactory(BaseFactory):

    def create(self, user, values):
        new_item = BaseFactory.create(self, user, values)
        return new_item


class Comment(BaseItem, Meta, Nested, Owned, Base):
    """Docstring for comment extension"""

    __tablename__ = 'comments'
    """Name of the table in the database for this modul. Do not
    change!"""
    _modul_id = None
    """Will be set dynamically. See include me of this modul"""

    # Define columns of the table in the database
    id = sa.Column(sa.Integer, primary_key=True)

    # Define relations to other tables
    text = sa.Column(sa.Text)

    @classmethod
    def get_item_factory(cls):
        return CommentFactory(cls)


class Commented(object):
    """Mixin to add comment functionallity to a modul. Adding this Mixin
    the item of a modul will have a "comments" relationship containing all
    the comment entries for this item."""

    @declared_attr
    def comments(cls):
        tbl_name = "nm_%s_comments" % cls.__name__.lower()
        nm_table = sa.Table(tbl_name, Base.metadata,
                            sa.Column('iid', sa.Integer,
                                      sa.ForeignKey(cls.id)),
                            sa.Column('cid', sa.Integer,
                                      sa.ForeignKey("comments.id")))
        comments = sa.orm.relationship(Comment,
                                       secondary=nm_table, cascade="all")
        return comments

    @classmethod
    def create_handler(cls, request, item):
        cls.update_handler(request, item)

    @classmethod
    def update_handler(cls, request, item):
        """Will add a comment entry for the updated item if the request
        contains a parameter 'comment'.  The mapper and the target
        parameter will be the item which inherits this commented mixin.

        :request: Current request
        :item: Item handled in the update.
        """
        log.debug("Called update_handler for %s" % cls)
        user_comment = request.params.get('comment')
        if user_comment:
            factory = Comment.get_item_factory()
            comment = factory.create(request.user, {})
            comment.text = user_comment
            item.comments.append(comment)
        return item
