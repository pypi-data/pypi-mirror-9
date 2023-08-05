from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings as base_settings

try:
    from django.utils.module_loading import import_string
except ImportError:
    from django.utils.module_loading import import_by_path as import_string


class Settings(object):

    SIRDJANGO_RENDER_MARKDOWN = 'sirdjango.markdown.render'
    SIRDJANGO_DEFAULT_BLOCKS = [
        'sirdjango.blocks.TextBlock',
        'sirdjango.blocks.VideoBlock'
    ]
    SIRDJANGO_MEDIA = {
        'js': [
            'sirdjango/js/jquery.js',
            'sirdjango/js/underscore.js',
            'sirdjango/js/eventable.js',
            'sirdjango/js/sir-trevor.js',
        ],
        'css': {'screen': [
            'sirdjango/css/sir-trevor.css',
            'sirdjango/css/sir-trevor-icons.css',
        ]},
    }

    def get_default_blocks(self):
        for block_string in self.SIRDJANGO_DEFAULT_BLOCKS:
            block_class = import_string(block_string)
            yield block_class()

    def __getattribute__(self, name):
        if hasattr(base_settings, name):
            return getattr(base_settings, name)
        return super(Settings, self).__getattribute__(name)


settings = Settings()
