from django import template
from django.template.loader import get_template

from bs4 import BeautifulSoup

from mezzanine.conf import settings
from mezzanine.pages.models import Page
from articles.models import Article
register = template.Library()


@register.assignment_tag
def section_article(section):
    try:
        return Article.objects.get(section__iexact=section)
    except:
        return None


@register.simple_tag
def section_children(section,
                     tpl="pages/articles/section.html",
                     limit=settings.MAX_PAGING_LINKS,
                     offset=0):
    """
    :param section:
    :param tpl:
    :param limit:
    :param offset:
    :return: rendered html with children of given section article
    """
    t = get_template(tpl)
    try:
        articles = Article.objects.get(
            section__iexact=section).children.all().order_by(
            '_order')[offset:offset+limit-1]
        return t.render(template.Context({
            "articles": articles,
            "section": section,
        }))
    except:
        return ''


@register.simple_tag
def section_articles(section,
                     tpl="pages/articles/section.html",
                     limit=settings.MAX_PAGING_LINKS,
                     offset=0):
    t = get_template(tpl)
    articles = Article.objects.filter(
        sections__section=section)[offset:offset+limit]
    return t.render(template.Context({
        "articles": articles,
        "section": section,
    }))


@register.assignment_tag
def pages_list(page):
    """
    :return: list of pages or queryset default ordered by pub date desc
    descendat to page.
    """

    return Page.objects.all().order_by('-publish_date')[:25]


@register.simple_tag
def parse_images(html, width=100, height=100, usersize=True,
                 tpl="pages/articles/lightbox.html",
                 strip_parent_p=True):
    """
    :param html: html string to parse.
    :param width: new image width.
    :param height: new image height.
    :param usersize: whether to parse width/height attributes from img tag.
    :param tpl: path to template for img tag replacer.
    :return: string with modified html content.

    Search for img tags and replace it with code for displaying images with
    declared size and add lightbox functionality etc.
    """

    t = get_template(tpl)
    soup = BeautifulSoup(html)
    imgs = soup.find_all("img")
    if imgs and width and height:
        for img in imgs:
            if "src" in img.attrs:
                c = {
                    "width": width,
                    "height": height,
                    "src": img.attrs.pop("src")}
                if usersize:
                    if "width" in img.attrs:
                        c["width"] = img.attrs.pop("width")
                    if "height" in img.attrs:
                        c["height"] = img.attrs.pop("height")
                for attr, value in img.attrs.items():
                    c[attr] = value
                new_img = BeautifulSoup(
                    t.render(template.Context(c)))

                if strip_parent_p:
                    pps = img.find_parents("p")
                    for pp in pps:
                        pp.unwrap()

                img.replace_with(new_img)


    retHtml = str(soup).replace(
        "<html><head></head><body>", "").replace(
        "</body></html>", "")
    return retHtml
