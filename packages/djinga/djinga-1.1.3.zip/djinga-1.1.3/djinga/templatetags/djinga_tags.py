"""
Extends the Django 'extends' template tag
This allows a django template to extend from a Jinja2 template if the extension
of a template is in settings.JINJA2_JJ_EXTS

Largely inspired from Kyle Rimkus' solution
http://concentricsky.com/blog/2013/jan/extending-jinja2-django-templates
"""


import re

from django import template
from django.template.loader_tags import do_extends

from ..engines import engines

register = template.Library()


@register.simple_tag
def block_super():
    return ''


@register.tag(name="extends")
def do_extends_jinja(parser, token):

    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("'%s' takes one argument" % bits[0])

    tmpl = bits[1][1:-1]
    if engines['djinga'].env.use_jinja(tmpl):
        # extends a Jinja2 template
        nodelist = parser.parse()
        return JinjaNode(tmpl, nodelist)
    else:
        # extends a Django template, use Django's do_extend
        return do_extends(parser, token)


class JinjaNode(template.Node):

    def __init__(self, template, nodelist):
        self.parent_template = template
        self.nodelist = nodelist

    def render(self, context):
        output_string = '{%% extends "%s" %%}' % self.parent_template
        for node in self.nodelist:
            if node.__class__.__name__ == 'BlockNode':
                # Replace dashes in block names because they aren't allowed
                # in jinja2
                node_name = node.name.replace('-', '_')
                # Go ahead and render this node
                rendered_node = node.render(context)
                r = re.compile(r'\{\{\s*super\(\)\s*\}\}')
                spr = '' if re.search(r, rendered_node) else ''
                rendered_node = re.sub(r, '', rendered_node)
                # wrap blocks in a {{ raw }} tag in case we need to display
                # raw template tags (eg. templates edited in an admin page)
                output_string += '{%% block %s %%}%s{%% raw %%} %s ' \
                                 '{%% endraw %%}{%% endblock %%}' % \
                                 (node_name, spr, rendered_node)
            else:
                output_string += node.render(context)
        output_template = engines['djinga'].env.from_string(output_string)
        output_template.name = self.parent_template
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        return output_template.render(context_dict)
