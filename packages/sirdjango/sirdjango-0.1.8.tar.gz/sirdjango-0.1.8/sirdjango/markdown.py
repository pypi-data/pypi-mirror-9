from __future__ import absolute_import, unicode_literals

import markdown


def render(input):
    return markdown.markdown(input)
