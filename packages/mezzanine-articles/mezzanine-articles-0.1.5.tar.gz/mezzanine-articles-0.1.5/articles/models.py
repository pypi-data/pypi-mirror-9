# -*- coding: UTF-8 -*-
import os
from string import punctuation
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from future.utils import native
from io import BytesIO
from mezzanine.core.fields import FileField
from mezzanine.core.managers import SearchableManager
from mezzanine.core.models import Orderable, RichText
from mezzanine.pages.models import Page
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.models import upload_to
from zipfile import ZipFile


GALLERIES_UPLOAD_DIR = "galleries"
if settings.PACKAGE_NAME_FILEBROWSER in settings.INSTALLED_APPS:
    fb_settings = "%s.settings" % settings.PACKAGE_NAME_FILEBROWSER
    try:
        GALLERIES_UPLOAD_DIR = import_dotted_path(fb_settings).DIRECTORY
    except ImportError:
        pass


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
        upload_to=upload_to("article.ArticleImage.file", "articles"))
    description = models.CharField(
        _("Description"), max_length=5000, blank=True,)

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
        upload_to=upload_to("articles.ArticleImage.file", "articles"),
        verbose_name=_("cover"),
        help_text=_("Image for visually signing article."))
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

    def save(self, delete_zip_import=True, *args, **kwargs):
        """
        If a zip file is uploaded, extract any images from it and add
        them to the gallery, before removing the zip file.
        """
        super(Article, self).save(*args, **kwargs)
        if self.zip_import:
            zip_file = ZipFile(self.zip_import)
            for name in zip_file.namelist():
                data = zip_file.read(name)
                try:
                    from PIL import Image
                    image = Image.open(BytesIO(data))
                    image.load()
                    image = Image.open(BytesIO(data))
                    image.verify()
                except ImportError:
                    pass
                except:
                    continue
                name = os.path.split(name)[1]
                # This is a way of getting around the broken nature of
                # os.path.join on Python 2.x. See also the comment below.
                if isinstance(name, bytes):
                    tempname = name.decode('utf-8')
                else:
                    tempname = name

                # A gallery with a slug of "/" tries to extract files
                # to / on disk; see os.path.join docs.
                slug = self.slug if self.slug != "/" else ""
                path = os.path.join(GALLERIES_UPLOAD_DIR, slug, tempname)
                try:
                    saved_path = default_storage.save(path, ContentFile(data))
                except UnicodeEncodeError:
                    from warnings import warn
                    warn("A file was saved that contains unicode "
                         "characters in its path, but somehow the current "
                         "locale does not support utf-8. You may need to set "
                         "'LC_ALL' to a correct value, eg: 'en_US.UTF-8'.")
                    # The native() call is needed here around str because
                    # os.path.join() in Python 2.x (in posixpath.py)
                    # mixes byte-strings with unicode strings without
                    # explicit conversion, which raises a TypeError as it
                    # would on Python 3.
                    path = os.path.join(GALLERIES_UPLOAD_DIR, slug,
                                        native(str(name, errors="ignore")))
                    saved_path = default_storage.save(path, ContentFile(data))
                self.images.add(ArticleImage(file=saved_path))
            if delete_zip_import:
                zip_file.close()
                self.zip_import.delete(save=True)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
