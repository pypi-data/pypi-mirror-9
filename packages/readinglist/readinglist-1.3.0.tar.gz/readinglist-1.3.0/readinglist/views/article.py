from cornice import resource
import colander
from colander import SchemaNode, String
from pyramid import httpexceptions

from cliquet import errors
from cliquet.resource import crud, BaseResource, ResourceSchema
from cliquet.utils import strip_whitespace, native_value
from cliquet.schema import URL, TimeStamp

TITLE_MAX_LENGTH = 1024


class DeviceName(SchemaNode):
    """String representing the device name."""
    schema_type = String
    validator = colander.Length(min=1)

    def preparer(self, appstruct):
        return strip_whitespace(appstruct)


class ArticleTitle(SchemaNode):
    """String representing the title of an article."""
    schema_type = String
    validator = colander.Length(min=1, max=TITLE_MAX_LENGTH)

    def preparer(self, appstruct):
        if appstruct:
            # Strip then truncate the title to TITLE_MAX_LENGTH
            return strip_whitespace(appstruct)[:TITLE_MAX_LENGTH]
        else:
            return appstruct


class ArticleSchema(ResourceSchema):
    """Schema for a reading list article."""

    url = URL()
    preview = URL(missing=None)
    title = ArticleTitle()
    added_by = DeviceName()
    added_on = TimeStamp()
    stored_on = TimeStamp()

    archived = SchemaNode(colander.Boolean(), missing=False)
    favorite = SchemaNode(colander.Boolean(), missing=False)
    unread = SchemaNode(colander.Boolean(), missing=True)
    is_article = SchemaNode(colander.Boolean(), missing=True)
    excerpt = SchemaNode(String(), missing="")

    read_position = SchemaNode(colander.Integer(), missing=0,
                               validator=colander.Range(min=0))
    marked_read_by = DeviceName(missing=None)
    marked_read_on = TimeStamp(auto_now=False)
    word_count = SchemaNode(colander.Integer(), missing=None)
    resolved_url = URL(missing=None)
    resolved_title = ArticleTitle(missing=None)

    class Options:
        readonly_fields = ('url', 'stored_on') + \
            ResourceSchema.Options.readonly_fields
        unique_fields = ('url', 'resolved_url') + \
            ResourceSchema.Options.unique_fields


@crud()
class Article(BaseResource):
    mapping = ArticleSchema()

    def put(self):
        response = errors.http_error(
            httpexceptions.HTTPMethodNotAllowed(),
            errno=errors.ERRORS.METHOD_NOT_ALLOWED)
        raise response

    def process_record(self, new, old=None):
        """Operate changes on submitted record.
        This implementation represents the specifities of the *Reading List*
        article resource.

        In a future version, URL resolution (*redirects*) and article title
        obtention (*HTML content*) will be performed here.

        Contrary to article content fetching, this fields resolution has to
        be performed synchronously (i.e. withing request/response cycle) during
        article creation, otherwise unicity of ``resolved_url`` cannot be
        guaranteed.

        :note:

            This could moved to a specific end-point, in order to keep the
            article API aligned with behaviour generic resources.
        """
        if old:
            # Read position should be superior
            if old['read_position'] > new['read_position']:
                new['read_position'] = old['read_position']

            # Marking as read requires device info
            if old['unread'] and not new['unread']:
                if not any((new['marked_read_on'], new['marked_read_by'])):
                    error = 'Missing marked_read_by or marked_read_on fields'
                    errors.raise_invalid(self.request, name='unread',
                                         description=error)

            # Device info is ignored if already read
            if not old['unread']:
                new['marked_read_on'] = old['marked_read_on']
                new['marked_read_by'] = old['marked_read_by']

        # In this first version, do not resolve url and title.
        if new['resolved_title'] is None:
            new['resolved_title'] = new['title']
        if new['resolved_url'] is None:
            new['resolved_url'] = new['url']

        # Reset info when article is marked as unreadd
        if new['unread']:
            new['marked_read_on'] = None
            new['marked_read_by'] = None
            new['read_position'] = 0

        return new

    @resource.view(permission='readwrite')
    def collection_post(self, *args, **kwargs):
        try:
            return super(Article, self).collection_post(*args, **kwargs)
        except httpexceptions.HTTPConflict as e:
            self.request.response.status_code = 200
            return e.existing

    def update_record(self, old, new, changes=None):
        """Update existing record."""
        new_record = super(Article, self).update_record(old, new, changes)
        body_behavior = self.request.headers.get(
            'Response-Behavior', 'full').lower()

        changed = [k for k in changes.keys()
                   if old.get(k) != new.get(k)]

        if body_behavior == 'full':
            return new_record
        elif body_behavior == 'light':
            return {k: new_record[k] for k in changed}
        elif body_behavior == 'diff':
            return {k: new_record[k] for k in changed
                    if native_value(changes.get(k)) != new_record.get(k)}
