import cgi
import ringo.lib.security as security
from ringo.lib.renderer.form import FieldRenderer


class CommentRenderer(FieldRenderer):
    """Custom Renderer for the comment listing"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)

    def _render_info(self, comment):
        html = []
        html.append("<small>")
        #html.append('<a href="/comments/read/%s">#%s</a>'
        #            % (comment.id, comment.id))
        #html.append(" | ")
        str_updated = comment.updated.strftime("%y.%m.%d %H:%M")
        str_created = comment.created.strftime("%y.%m.%d %H:%M")
        html.append(str_created)
        html.append(" | ")
        html.append("<bold>"
                    + cgi.escape(unicode(comment.owner.profile[0]))
                    + "</bold>")
        if str_updated != str_created:
            html.append(" | (")
            html.append(str_updated)
            html.append(")</small>")
        return html

    def _render_body(self, comment):
        html = []
        html.append(cgi.escape(comment.text).replace('\n', '<br>') or "")
        return html

    def render(self):
        _ = self.translate
        html = []
        comments = []
        for comment in self._field._form._item.comments:
            if security.has_permission('read',
                                       comment,
                                       self._field._form._request):
                comments.append(comment)
        if not self._field.is_readonly():
            html.append('<label for="new-comment" class="control-label">')
            html.append(_('New entry'))
            html.append('</label>')
            html.append(('<textarea class="form-control" id="new-comment" '
                         'name="comment"></textarea>'))
            html.append('</br>')
        html.append('<label for="">%s (%s)</label>'
                    % (cgi.escape(self._field.label), len(comments)))
        for comment in comments[::-1]:
            html.append('<input type="checkbox" name="%s" value="%s"'
                        ' style="display:none"/>'
                        % (cgi.escape(self._field.name), comment.id))
            html.append('<div class="readonlyfield">')
            html.append("<table>")
            html.append("<tr >")
            html.append("<td>")
            html.extend(self._render_body(comment))
            html.append("</td>")
            html.append("<tr>")
            html.append('<td>')
            html.extend(self._render_info(comment))
            html.append("</td>")
            html.append("</tr>")
            html.append("</table>")
            html.append("</div>")
        return "".join(html)
