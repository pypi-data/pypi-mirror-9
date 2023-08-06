from frasco import Feature, action, ActionsView, current_app, Markup
from frasco.utils import remove_yaml_frontmatter, wrap_in_markup
from frasco.templating import render_layout, jinja_fragment_extension, get_template_source
import markdown
import os


class MarkdownView(ActionsView):
    def __init__(self, layout=None, **kwargs):
        super(MarkdownView, self).__init__(**kwargs)
        self.layout = layout

    def render(self, **kwargs):
        if self.template is None:
            return None

        source = get_template_source(current_app, self.template)
        html = current_app.features.markdown.convert(remove_yaml_frontmatter(source))

        if self.layout is None:
            return html
        return render_layout(self.layout, html, **kwargs)


@jinja_fragment_extension("markdown")
def MarkdownJinjaExtension(caller, **kwargs):
    return current_app.features.markdown.convert(caller(), **kwargs)


class MarkdownFeature(Feature):
    name = "markdown"
    view_files = [("*.md", MarkdownView)]
    defaults = {"extensions": {},
                "output_format": "html5",
                "safe_mode": False,
                "html_replacement_text": "[HTML REMOVED]"}

    def init_app(self, app):
        app.jinja_env.add_extension(MarkdownJinjaExtension)
        app.add_template_filter(wrap_in_markup(self.convert), "markdown")

    @action("markdown_to_html", default_option="content")
    def convert(self, content, **kwargs):
        kwargs.setdefault('extensions', self.options["extensions"].keys())
        kwargs.setdefault('extension_configs', self.options["extensions"])
        kwargs.setdefault('output_format', self.options["output_format"])
        kwargs.setdefault('safe_mode', self.options["safe_mode"])
        kwargs.setdefault('html_replacement_text', self.options["html_replacement_text"])
        return markdown.markdown(content, **kwargs)