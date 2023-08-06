#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from authors.models import Author
from autoslug.fields import AutoSlugField
from cms.models import Page
from cms.models.fields import PlaceholderField
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import striptags, truncatewords_html
from django.utils.translation import ugettext_lazy as _
from pegasus.utils import cache_for
from menus.menu_pool import menu_pool
from model_utils import Choices
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager
import cachemodel


class CelerityPrioritizedContentMixin(models.Model):
    HELP_TEXT = _('Used to prioritize topics and issues and to fine-tune '
                  'search results.')

    PRIORITY_CHOICES = Choices(
        (1, 'Highest', _('Highest')),
        (2, 'High', _('High')),
        (3, 'Medium', _('Medium')),
        (4, 'Low', _('Low')),
        (5, 'Lowest', _('Lowest')),)

    priority = models.IntegerField(choices=PRIORITY_CHOICES,
                                   default=PRIORITY_CHOICES.Medium,
                                   db_index=True,
                                   help_text=HELP_TEXT)

    class Meta:
        abstract = True
        ordering = ('priority',)


class CelerityFeaturedContentMixin(models.Model):
    HELP_TEXT = _('Features a piece of content, bringing it to the top of '
                  'search results, content lists, and backfilled modules.')

    featured = models.BooleanField(default=False,
                                   db_index=True,
                                   help_text=HELP_TEXT)

    class Meta:
        abstract = True
        ordering = ('-featured',)


class CelerityContentNode(CelerityPrioritizedContentMixin,
                          CelerityFeaturedContentMixin,
                          models.Model):
    slug = AutoSlugField(populate_from='headline',
                         unique=True,
                         null=False,
                         blank=False)
    headline = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        abstract = True
        ordering = ('-featured', 'priority',)

    def __unicode__(self):
        return u'{title}'.format(title=self.headline)

    def get_absolute_url(self):
        raise NotImplementedError(
            'The CelerityContentNode subclass must implement "get_absolute_url"!')

    @property
    def name(self):
        return self.headline

    @property
    def url(self):
        return self.get_absolute_url()


class CelerityContentType(CelerityContentNode,
                          TimeStampedModel,
                          models.Model):
    """ An abstract base class to define common attributes and operations
        for Celerity's CMS content types."""

    article_type = models.ForeignKey('ArticleType',
                                     null=False,
                                     blank=False)
    issues = models.ManyToManyField('Issue')
    author = models.ForeignKey(Author)
    keywords = TaggableManager(blank=True)
    date_published = models.DateTimeField(db_index=True)

    class Meta:
        abstract = True
        index_together = (('featured', 'priority', 'date_published',),)
        ordering = ('-featured', 'priority', '-date_published',)

    @property
    @cache_for(minutes=5)
    def contact_name(self):
        return self.author.full_name

    @property
    @cache_for(minutes=5)
    def image(self):
        """ Gets a visual representation for the article. Usually, this is a
            thumbnail image to use for promoting the article."""

        if self.image_lead:
            self.image_alt_text = self.image_lead_alt_text
            return self.image_lead.url

        if hasattr(self, 'body'):
            for plugin in self.body.get_plugins():
                if plugin.plugin_type == 'PicturePlugin':
                    self.image_alt_text = self.image_lead_alt_text
                    return plugin.picture.image.url

        # If we can't find an image in the article, default to the Topic's
        # image, if one is assigned.
        if self.topic:
            self.image_alt_text = self.topic.image_alt_text
            return self.topic.image and self.topic.image.url or u''
        return None

    # NOTE: It's tempting to cache the 'full_text_body' function, but beware:
    # it can eat up a LOT of memory.
    @property
    def full_text_body(self):
        _full_text = ''
        for plugin in self.body.get_plugins():
            if plugin.plugin_type == 'TextPlugin':
                _full_text += plugin.text.body
        return striptags(_full_text)

    @cache_for(minutes=30)
    def summary(self, num_words=15):
        """ Gets a text summary of the article. This is often used as the
            default 'promo text' for an article."""

        text_to_summarize = u''

        if hasattr(self, 'subheading') and self.subheading:
            text_to_summarize = self.subheading
        elif hasattr(self, 'full_text_body'):
            text_to_summarize = self.full_text_body

        return striptags(
            truncatewords_html(text_to_summarize, num_words)).strip()

    @property
    @cache_for(minutes=3)
    def issue(self):
        return self.issues.first()

    @property
    def topic(self):
        try:
            return Topic.cached.get(pk=self.issue.topic_id)
        except:
            return None


class Topic(CelerityContentNode, cachemodel.CacheModel):
    image = models.ImageField(upload_to='topics', blank=True, null=True)
    image_alt_text = models.CharField(max_length=255, blank=True, null=True)

    @cache_for(minutes=5)
    def get_absolute_url(self):
        try:
            return '{search_url}?topic={topic}'.format(
                search_url=reverse('celerity-search'),
                topic=self.slug)
        except NoReverseMatch as e:
            return ''

    def publish(self):
        # Used by cachemodel to publish an index for this object in Django's
        # cache.
        super(Topic, self).publish()
        self.publish_by('slug',)

    @property
    def articles(self):
        return Article.objects.filter(issues__topic=self).order_by(
            'featured').order_by('priority')


class Issue(CelerityContentNode):
    topic = models.ForeignKey(Topic, null=False, blank=False)

    def __unicode__(self):
        return '{topic} - {issue}'.format(
            topic=self.topic.name,
            issue=self.name)

    @cache_for(minutes=30)
    def get_absolute_url(self):
        try:
            return '{search_url}?topic={topic}&issue={issue}'.format(
                search_url=reverse('celerity-search'),
                topic=self.topic.slug,
                issue=self.slug)
        except NoReverseMatch as e:
            return ''

    @property
    def articles(self):
        """ Returns a list of prioritized articles (sorted by 'Featured'
            and then 'priority'."""
        return Article.objects.filter(issue=self).order_by(
            'featured').order_by('priority')


@receiver(models.signals.post_save, sender=Issue)
@receiver(models.signals.post_save, sender=Topic)
@receiver(models.signals.post_delete, sender=Issue)
@receiver(models.signals.post_delete, sender=Topic)
def bust_menu_cache(sender, instance, **kwargs):
    # The will allow the content menu to be rebuilt immediately if a new Issue
    # or Topic is created, or if an existing one is modified.
    menu_pool.clear()


class ArticleType(models.Model):
    name = models.CharField(max_length=100,
                            null=False,
                            blank=False,
                            default='')
    slug = AutoSlugField(populate_from='name',
                         unique=True,
                         null=False,
                         blank=False)

    def __unicode__(self):
        return self.name

    @classmethod
    @cache_for(hours=12)
    def get_media_article_types(cls):
        return cls.objects.filter(slug='pegasus-in-the-news')

    @classmethod
    @cache_for(hours=12)
    def get_work_article_types(cls):
        return cls.objects.filter(slug__in=['legislative-issue',
                                            'results',
                                            'litigation',
                                            'research',])

class Article(CelerityContentType):
    date_label = models.DateTimeField()

    image_lead = models.ImageField(upload_to="articles", blank=True, null=True)
    image_lead_alt_text = models.CharField(max_length=255, null=True, blank=True)

    subheading = models.CharField(max_length=255, blank=True, null=True)
    lead = models.TextField(blank=True, null=True)

    body = PlaceholderField('article_body')

    show_comments = models.BooleanField(default=True, blank=False, null=False)

    source = models.CharField(max_length=255, blank=True, null=True)

    @cache_for(minutes=30)
    def get_absolute_url(self):
        if self.issue and self.topic:
            try:
                return reverse('content:article_detail',
                    current_app='content',
                    kwargs={'topic_slug': self.topic.slug,
                            'issue_slug': self.issue.slug,
                            'slug': self.slug})
            except NoReverseMatch as e:
                return ''
        return ''


class Case(CelerityContentType):
    date_label = models.DateTimeField()

    image_lead = models.ImageField(upload_to="articles", blank=True, null=True)
    image_lead_alt_text = models.CharField(max_length=255, null=True, blank=True)

    subheading = models.CharField(max_length=255, blank=True, null=True)
    lead = models.TextField(blank=True, null=True)

    body = PlaceholderField('article_body')

    show_comments = models.BooleanField(default=True, blank=False, null=False)

    source = models.CharField(max_length=255, blank=True, null=True)

    last_step = models.TextField(blank=True, null=True)
    next_step = models.TextField(blank=True, null=True)

    legal_team = models.ManyToManyField(Author, through='LegalTeam', related_name="cases")

    def __unicode__(self):
        return u"%s" % self.headline

    @cache_for(minutes=30)
    def get_absolute_url(self):
        if self.issue and self.topic:
            try:
                return reverse('content:case_detail',
                    current_app='content',
                    kwargs={'topic_slug': self.topic.slug,
                            'issue_slug': self.issue.slug,
                            'slug': self.slug})
            except NoReverseMatch as e:
                return ''
        return ''

    @property
    @cache_for(minutes=30)
    def is_case(self):
        return True


class LegalTeam(models.Model):
    bio = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Author)
    case = models.ForeignKey(Case)

    def __unicode__(self):
        return "%s: %s" % (self.author, self.case)


class PromoPlacement(models.Model):
    HELP_TEXT = 'Show promo on all instances of the selected type'

    PROMO_POSITIONS = (
        ('left-rail', 'left-rail'),
        ('right-rail', 'right-rail'),
        ('middle', 'middle'),
    )

    # BEGIN - generic relation definition
    content_type = models.ForeignKey(ContentType,
                                     blank=True,
                                     null=True,
                                     limit_choices_to={'model__in':
                                        ['case', 'event', 'article', 'page',
                                         'author']},
                                     help_text=HELP_TEXT)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    # END - generic relation definition

    position = models.CharField(max_length=25,
                                choices=PROMO_POSITIONS,
                                null=True,
                                blank=True,
                                db_index=True)
    promo = models.ForeignKey('Promo', null=False, blank=False)

    class Meta:
        verbose_name = 'Promo Placement'
        verbose_name_plural = 'Promo Placements'

    def __unicode__(self):
        return u'{page}:{position} -> {promo}'.format(
            page=self.content_object,
            position=self.position,
            promo=self.promo.name)

    def save(self, *args, **kwargs):
        PAGE_CONTENT_TYPE = ContentType.objects.get_for_model(Page)
        if self.content_type == PAGE_CONTENT_TYPE:
            # always use the public page for the relationship
            page = Page.objects.get(pk=self.object_id)
            self.object_id = page.get_public_object().pk
        super(PromoPlacement, self).save(*args, **kwargs)

    @property
    def promo_label(self):
        return self.promo.promo_label

    @property
    def image(self):
        return self.promo.image

    @property
    def image_alt_text(self):
        return self.promo.image_alt_text

    @property
    def title(self):
        return self.promo.title

    @property
    def url(self):
        return self.promo.url

    @property
    def view_all_label(self):
        return self.promo.view_all_label

    @property
    def view_all_url(self):
        return self.promo.view_all_url

    @property
    def text(self):
        return self.promo.text

    @property
    def date(self):
        return self.promo.date

    @property
    def download_link(self):
        return self.promo.download_link

class Promo(models.Model):
    HELP_TEXT = 'Show promo on all instances of the selected type'

    promo_label = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='promos',
                              null=True,
                              blank=True)
    image_alt_text = models.CharField(max_length=255,
                                      null=True,
                                      blank=True)
    title = models.CharField(max_length=50,
                             null=True,
                             blank=True)
    url = models.URLField(blank=True, null=True)
    view_all_label = models.CharField(max_length=50,
                                      null=True,
                                      blank=True)
    view_all_url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    download_link = models.URLField(blank=True, null=True)

    def __unicode__(self):
        """
        FIXME: Is the below statement still accurate?
        ...
        No fields are required so drop down through possible
        fields to attempt to find a populated relevant field
        to use for display
        """

        if self.title:
            return u"%s" % self.title

        if self.promo_label:
            return u"%s" % self.promo_label

        if self.text:
            return u"%s" % self.text[:20]

        if self.date:
            return u"%s" % self.date

        return u"Promo"

    @property
    def name(self):
        return self


class Event(CelerityContentType):
    title = models.CharField(max_length=255)
    body = PlaceholderField('event_body')
    event_image = models.ImageField(upload_to='event', blank=True, null=True)
    event_image_alt_text = models.CharField(max_length=255, null=True, blank=True)
    event_url = models.URLField(blank=True, null=True)
    url_label = models.CharField(max_length=255, blank=True, null=True)
    fee = models.CharField(max_length=50, blank=True, null=True)
    location_info = models.TextField(blank=True, null=True)
    event_date = models.DateTimeField()

    def __unicode__(self):
        return u"%s" % self.title

    @property
    @cache_for(minutes=5)
    def contact_image(self):
        if self.author.image:
            return self.author.image

    @cache_for(minutes=30)
    def get_absolute_url(self):
        if self.issue and self.topic:
            try:
                return reverse('content:event_detail',
                    current_app='content',
                    kwargs={'topic_slug': self.topic.slug,
                            'issue_slug': self.issue.slug,
                            'slug': self.slug})
            except NoReverseMatch as e:
                return ''
        return ''

    @property
    @cache_for(minutes=5)
    def image(self):
        """ Gets a visual representation for the article. Usually, this is a
            thumbnail image to use for promoting the article."""

        if self.event_image:
            return self.event_image.url

        return CelerityContentType.image.fget(self) # call parent property
