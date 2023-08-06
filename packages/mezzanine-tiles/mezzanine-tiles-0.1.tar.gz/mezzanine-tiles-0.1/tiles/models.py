# -*- coding: UTF-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.fields import FileField
from mezzanine.core.models import RichText
from mezzanine.pages.models import Page
from mezzanine.utils.models import upload_to


class TileSection(Page):
    section = models.CharField(
        verbose_name=_("section"), max_length=50, unique=True,
        help_text="Name used in for example class= attribute.")

    def __unicode__(self):
        return u'%s' % self.title


class Tile(Page, RichText):
    front_image = FileField(
        max_length=200, format="Image", blank=True, null=True,
        upload_to=upload_to("antennas.GalleryImage.file", "illustrations"))
    background_image = FileField(
        max_length=200, format="Image", blank=True, null=True,
        upload_to=upload_to("antennas.GalleryImage.file", "illustrations"))
    link_to = models.URLField(blank=True, null=True,)
    sections = models.ManyToManyField(
        TileSection, _("sections"),
        related_name=u"tile_sections",
        null=True, blank=True,)

    def save(self, *args, **kwargs):
        super(Tile, self).save(*args, **kwargs)
        parent = self.parent
        while True:
            if parent:
                if parent.content_model == "section":
                    if not self.sections.filter(section=parent.section.section):
                        self.sections.add(parent.section)
                    break
                else:
                    parent = parent.parent
            else:
                break

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        verbose_name = _("Tile")
        verbose_name_plural = _("Tiles")
