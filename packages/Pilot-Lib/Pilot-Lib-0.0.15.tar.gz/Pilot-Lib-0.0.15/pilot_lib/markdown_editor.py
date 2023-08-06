"""
Pilot Markdown Editor

To render the markdown:
{{ text | markdown }}

require: mistune
"""

import os
import jinja2
from flask_pilot import Pilot
from flask.ext.assets import Environment, Bundle

NAME = "Markdown Editor"
__version__ = "0.3"

_dir_ = os.path.dirname(__file__)


class MarkdownEditor(object):
    """
    Register the templates
    """
    def __init__(self, app):
        template_dir = os.path.join(_dir_, "templates")
        my_loader = jinja2.ChoiceLoader([
            app.jinja_loader,
            jinja2.FileSystemLoader(template_dir)
        ])
        app.jinja_loader = my_loader

        env = Pilot.assets
        env.load_path = [
            Pilot._app.static_folder,
            os.path.join(_dir_, 'static'),
        ]
        env.register(
            'markdown_editor_js',
            Bundle(
                "MarkdownEditor/js/markdown.js",
                "MarkdownEditor/js/to-markdown.js",
                "MarkdownEditor/js/bootstrap-markdown.js",
                output='markdown-editor.js'
            )
        )
        env.register(
            'markdown_editor_css',
            Bundle(
                'MarkdownEditor/css/bootstrap-markdown.min.css',
                'MarkdownEditor/css/style.css',
                output='markdown-editor.css'
            )
        )
