from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language_from_request
from wq.db.patterns.base import SerializableGenericRelation

import swapper
swapper.set_app_prefix('mark', 'WQ')

from django.conf import settings


class BaseMarkdownType(models.Model):
    name = models.CharField(max_length=100)

    @classmethod
    def get_current(cls, request=None):
        if request:
            try:
                kwargs = cls.get_current_filter(request)
                return cls.objects.get(**kwargs)
            except cls.DoesNotExist:
                pass
        return cls.get_default()

    @classmethod
    def get_current_filter(cls, request):
        raise NotImplementedError()

    @classmethod
    def get_default(cls):
        markdowns = cls.objects.order_by('pk')
        if len(markdowns) > 0:
            return markdowns[0]

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class MarkdownType(BaseMarkdownType):
    @classmethod
    def get_current_filter(cls, request):
        lang = get_language_from_request(request)
        return {'name': lang}

    class Meta:
        swappable = swapper.swappable_setting('mark', 'MarkdownType')
        db_table = "wq_markdowntype"


class Markdown(models.Model):
    type = models.ForeignKey(swapper.get_model_name('mark', 'MarkdownType'))
    summary = models.CharField(max_length=255, null=True, blank=True)
    markdown = models.TextField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def __str__(self):
        return self.summary

    @property
    def html(self):
        from markdown import markdown
        extensions = getattr(settings, 'MARKDOWN_EXTENSIONS', [])
        return markdown(self.markdown, extensions)

    class Meta:
        db_table = "wq_markdown"


class MarkedModel(models.Model):
    markdown = SerializableGenericRelation(Markdown)

    def get_markdown(self, type):
        markdowns = self.markdown.filter(type=type)
        if len(markdowns) == 0:
            markdowns = self.markdown.order_by("type")
        if len(markdowns) > 0:
            return markdowns[0]
        return None

    def get_html(self, type):
        markdown = self.get_markdown(type)
        return markdown.html

    class Meta:
        abstract = True
