from django.db import models
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from filer.fields.image import FilerImageField


class Project(models.Model):

    title = models.CharField(_("Title"), max_length=200)
    subtitle = models.CharField(_("Subtitle"), max_length=200, blank=True)

    meta_keywords = models.CharField(_("Meta keywords"), max_length=500, help_text=_("Comma separated list"))
    meta_author = models.CharField(_("Meta author"), max_length=100)
    meta_description = models.CharField(_("Meta description"), max_length=155)

    google_analytics = models.CharField(_("Google Analytics"), max_length=50)

    site = models.OneToOneField(Site, verbose_name=_("Site"), help_text=_("Domain where the project belongs"))
    base_template = models.TextField()

    sections = models.ManyToManyField("Section", verbose_name=_("Sections"), through='SectionOrder')

    def __unicode__(self):
        return self.title


class GenericObject(models.Model):
    project = models.ManyToManyField(Project, verbose_name=_("Project"))

    published = models.BooleanField(_("Published"), default=False)


def get_generic_objects():
    values = [ o.model for o in ContentType.objects.all() if GenericObject in o.model_class().__bases__ ]
    return reduce(lambda q,value: q|models.Q(model=value), values, models.Q())


class Section(models.Model):

    title = models.CharField(_("Title"), max_length=200)
    icon = models.CharField(_("Icon"), max_length=20, help_text=_("Icons are built from font-awesome. Choose one from <a href='http://fortawesome.github.io/Font-Awesome/icons/'>fontawesome page</a>. Example, if you like the 'fa-users' icon, just write fa-users in this field"), null=True, blank=True)
    background_color = models.CharField(_("Background color"), max_length=9, help_text=("#xxxxxx"), null=True, blank=True)
    background_image = FilerImageField(null=True, blank=True, on_delete=models.SET_NULL)

    # limit = models.Q(app_label='projects', model='researcher') | models.Q(app_label='projects', model='article')
    content_type = models.ForeignKey(ContentType, verbose_name=_("Page content"), limit_choices_to=get_generic_objects, null=True, blank=True)

    def __unicode__(self):
        return self.title


class CTemplate(models.Model):

    title = models.CharField(_("Title"), max_length=200)
    content = models.TextField()
    project = models.ManyToManyField(Project, verbose_name=_("Project"))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")


class SectionOrder(models.Model):

    order = models.PositiveIntegerField(_("Order"))
    section = models.ForeignKey(Section, verbose_name=_("Section"))
    project = models.ForeignKey(Project, verbose_name=_("Project"))
    template = models.ForeignKey(CTemplate, verbose_name=_("Template"))
    on_menu = models.BooleanField(_("On menu"), default="True", help_text=_("Create a menu item in the navigation bar for this section"))

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")
        ordering = ("order",)
