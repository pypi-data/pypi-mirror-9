# -*- coding: UTF-8 -*-
from string import punctuation
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.fields import FileField
from mezzanine.core.managers import SearchableManager
from mezzanine.core.models import Orderable, RichText, Displayable
from mezzanine.pages.models import Page
from mezzanine.utils.models import upload_to


class LinkedPage(Orderable):
    article = models.ForeignKey("Article", related_name="article_links")
    page = models.ForeignKey(Page)

    @staticmethod
    def autocomplete_search_fields():
        return ("page__titles__icontains", "page_description__icontains",)


@python_2_unicode_compatible
class ArticleImage(Orderable):

    article = models.ForeignKey("Article", related_name="images")
    file = FileField(_("File"), max_length=200, format="Image",
        upload_to=upload_to("article.GalleryImage.file", "article"))
    description = models.CharField(
        _("Description"), max_length=1000, blank=True,)

    #objects = SearchableManager()
    #search_fields = ("description",)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        """
        If no description is given when created, create one from the
        file name.
        """
        if not self.id and not self.description:
            name = force_text(self.file.name)
            name = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            name = name.replace("'", "")
            name = "".join([c if c not in punctuation else " " for c in name])
            # str.title() doesn't deal with unicode very well.
            # http://bugs.python.org/issue6412
            name = "".join([s.upper() if i == 0 or name[i - 1] == " " else s
                            for i, s in enumerate(name)])
            self.description = name
        super(ArticleImage, self).save(*args, **kwargs)


class SectionManager(models.Manager):
    """
    :return:queryset with non empty section field
    """
    def get_queryset(self):
        return super(SectionManager, self).get_queryset().exclude(
            section__exact="",)


class Article(Page, RichText):
    """
    Default sections should be all from parents content ArticleSection
    """
    cover = FileField(
        max_length=200, format="Image", blank=True, null=True,
        upload_to=upload_to("articles.GalleryImage.file", "illustrations"),
        verbose_name=_("cover"),
        help_text=_("Image for visualy signing article."))
    zip_import = models.FileField(
        verbose_name=_("Zip import"), blank=True, null=True,
        upload_to=upload_to("articles.Article.zip_import", "articles"),
        help_text=_("Upload a zip file containing images, and "
                    "they'll be imported into this gallery."),)
    show_gallery = models.BooleanField(
        _("show gallery"), default=True,
        help_text=_("Controls when show or hide gallery on article page."))
    section = models.CharField(
        verbose_name=_("section"), max_length=50, blank=True, null=True,
        help_text=_("Name used in for example class= attribute."))
    sections = models.ManyToManyField(
        "self", verbose_name=_("sections"),
        null=True, blank=True,)

    objects = SearchableManager()
    section_list = SectionManager()

    def siblings(self):
        """
        :return:queryset with instances siblings
        """
        return self.parent.children.exclude(pk=self.id)

    def sections_csl(self):
        """
        :return: comma separated list of sections
        """
        sections = []
        if self.section:
            sectios.append(self.section)
        sections_csl = ', '.join(
            sections + self.sections.all().values_list('section', flat=True))
        print sections_csl
        return sections_csl

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
