from django.core.urlresolvers import reverse
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=False, blank=False)
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department)
    email = models.EmailField()
    image = models.ImageField(upload_to="authors", blank=True, null=True)
    bio = models.TextField()
    url = models.URLField(blank=True, null=True)

    order = models.IntegerField(default=1)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def full_name(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name)

    @property
    def name(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['order', ]
