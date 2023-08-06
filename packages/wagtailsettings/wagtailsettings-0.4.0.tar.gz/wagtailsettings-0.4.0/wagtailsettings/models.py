from django.db import models


class BaseSetting(models.Model):
    site = models.ForeignKey('wagtailcore.Site', unique=True, db_index=True,
                             editable=False)

    class Meta:
        abstract = True

    @classmethod
    def for_site(cls, site):
        instance, created = cls.objects.get_or_create(site=site)
        return instance
