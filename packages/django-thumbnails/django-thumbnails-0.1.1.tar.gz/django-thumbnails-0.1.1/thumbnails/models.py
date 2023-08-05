from django.db import models


class Source(models.Model):
    name = models.CharField(unique=True, max_length=255)


class ThumbnailMeta(models.Model):
    source = models.ForeignKey(Source, related_name='thumbnails')
    size = models.CharField(max_length=64)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        unique_together = ('source', 'size')
