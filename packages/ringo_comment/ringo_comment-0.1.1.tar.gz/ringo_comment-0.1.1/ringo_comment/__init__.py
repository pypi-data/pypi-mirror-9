import logging
from pyramid.i18n import TranslationStringFactory
from ringo.lib.i18n import translators
from ringo.lib.extension import register_modul
from ringo.lib.helpers import dynamic_import
from ringo.lib.renderer.form import add_renderers

from ringo_comment.lib.renderer import CommentRenderer
# Import models so that alembic is able to autogenerate migrations
# scripts.
from ringo_comment.model import Comment

log = logging.getLogger(__name__)

modul_config = {
    "name": "comment",
    "label": "",
    "clazzpath": "ringo_comment.model.Comment",
    "label_plural": "",
    "str_repr": "",
    "display": "",
    "actions": ["list", "read", "update", "create", "delete"]
}


def includeme(config):
    """Registers a new modul for ringo.

    :config: Dictionary with configuration of the new modul

    """
    modul = register_modul(config, modul_config)
    add_renderers({"comment": CommentRenderer})
    Comment._modul_id = modul.get_value("id")
    translators.append(TranslationStringFactory('ringo_comment'))
    config.add_translation_dirs('ringo_comment:locale/')

