from django import template
from datetime import datetime

from geelweb.django.editos.models import Edito

register = template.Library()


class EditoNode(template.Node):
    DEFAULT_TEMPLATE = 'editos/carousel.html'

    def __init__(self, template_file=None):
        if template_file:
            self.template = template_file
        else:
            self.template = self.DEFAULT_TEMPLATE

    def render(self, context):
        editos = Edito.objects.filter(active=1, display_from__lte=datetime.now(),
                                      display_until__gte=datetime.now())
        t = template.loader.get_template(self.template)
        return t.render(template.Context({'editos': editos}, autoescape=context.autoescape))


@register.tag
def editos(parser, token):
    """
    Retrieves diaplayable editos and render them using the provided template

    Syntax::

      {% editos ['template/file.html'] %}

    Exemple usage::

      {% editos %}
      {% editos 'editos/carousel.html' %}
    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                      "['path/to/template.html']" %
                      dict(tag_name=bits[0]))

    if len(bits) >= 1 and len(bits) <= 2:
        if len(bits) > 1:
            template_file = bits[1]
        else:
            template_file = None
        return EditoNode(template_file=template_file)
    else:
        raise template.TemplateSyntaxError(syntax_message)
