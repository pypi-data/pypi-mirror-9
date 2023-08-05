from __future__ import absolute_import, unicode_literals

import re
import six

from django.core.exceptions import ValidationError
from django.forms.widgets import MediaDefiningClass

from .conf import settings, import_string


def underscored(name):
    """
    A port of the SirTrevor.js `underscored` function. This transforms block
    names in to types for serialisation.
    """
    name = name.strip()
    name = re.sub(r'([a-z\d])([A-Z]+)', r'\1_\2', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name.lower()


class BaseBlock(six.with_metaclass(MediaDefiningClass, object)):

    name = None

    @property
    def block_type(self):
        return underscored(self.name)

    def render_json(self, json):
        raise NotImplementedError

    def clean(self, data):
        """
        Clean incoming JSON data.

        If the data are not valid, raises a ValidationError
        """
        return data

    def json_for_editing(self, data):
        """
        Process data for editing in a SirTrevor widget. Mostly not needed,
        except for RichTextArea emulation in Wagtail.
        """
        return data

class TextBlock(BaseBlock):
    name = 'Text'

    def clean(self, data):
        data = super(TextBlock, self).clean(data)
        if set(['text']) - set(data.keys()):
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        render_markdown = import_string(settings.SIRDJANGO_RENDER_MARKDOWN)
        return render_markdown(data['text'])


class VideoBlock(BaseBlock):
    name = 'Video'

    protocol = ''
    providers = {
        'vimeo': {
            'html': r'<iframe src="{protocol}//player.vimeo.com/video/{remote_id}?title=0&byline=0" width="580" height="320" frameborder="0"></iframe>',
            'remote_id': re.compile(r'^\d+$'),
        },
        'youtube': {
            'html': r'<iframe src="{protocol}//www.youtube.com/embed/{remote_id}" width="580" height="320" frameborder="0" allowfullscreen></iframe>',
            'remote_id': re.compile(r'^[a-zA-Z0-9_-]{10,12}$'),
        }
    }

    def clean(self, data):
        data = super(VideoBlock, self).clean(data)
        if set(['source', 'remote_id']) - set(data.keys()):
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        if data['source'] not in self.providers:
            raise ValidationError('Invalid video provider')
        provider = self.providers[data['source']]
        if provider['remote_id'].match(data['remote_id']) is None:
            raise ValidationError('Invalid video ID')
        return data

    def render_json(self, data):
        provider = self.providers[data['source']]
        return provider['html'].format(protocol=self.protocol,
                                       remote_id=data['remote_id'])
