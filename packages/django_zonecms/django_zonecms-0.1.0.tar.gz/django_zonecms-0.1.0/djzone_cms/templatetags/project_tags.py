from django import template
from django.template import Library, loader, Context
from django.contrib.sites.models import Site

import markdown

register = template.Library()

@register.simple_tag
def build_section(section):
    objects = None
    project = section.project

    if section.section.content_type:
        objects = section.section.content_type.model_class().objects.filter(project=project, published=True)


    t = template.Template(section.template.content)
    return t.render(Context({
        'project': project,
        'title': section.section.title,
        'backgroun_color': section.section.background_color,
        'icon': section.section.icon,
        'order': section.order,
        'objects': objects
    }))


@register.filter
def markdownify(text):
    return markdown.markdown(text)
