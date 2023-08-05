from django.template import Template, Context
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site

import models

def home(request):

    project = models.Project.objects.get(pk=get_current_site(request).project.pk)  # Everytime the page is reloaded, we want to force to reload the template (it may have changed)
    template = Template(project.base_template)

    return HttpResponse(template.render(Context({ 'project': project })))
