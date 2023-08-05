import re

from django.db import models
from path_helpers import path


class Version(models.Model):
    major = models.IntegerField()
    minor = models.IntegerField()
    micro = models.IntegerField()
    publish = models.BooleanField(default=False)

    def url(self):
        raise NotImplementedError

    def path(self):
        raise NotImplementedError

    class Meta:
        abstract = True
        ordering = ['major', 'minor', 'micro']

    def __unicode__(self):
        return u'%s (%s, %s, %s)' % (self.package, self.major, self.micro,
                self.minor)


class Package(models.Model):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)
