# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from parler.views import TranslatableSlugMixin, ViewUrlMixin
from taggit.models import Tag

from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_categories.models import Category
from aldryn_people.models import Person

from .models import Article


class EditModeMixin(object):
    """
    A mixin which sets the property 'edit_mode' with the truth value for
    whether a user is logged-into the CMS and is in edit-mode.
    """
    edit_mode = False

    def dispatch(self, request, *args, **kwargs):
        self.edit_mode = (
            self.request.toolbar and self.request.toolbar.edit_mode)
        return super(EditModeMixin, self).dispatch(request, *args, **kwargs)


class PreviewModeMixin(EditModeMixin):
    """
    If content editor is logged-in, show all articles. Otherwise, only the
    published articles should be returned.
    """
    def get_queryset(self):
        qs = Article.objects
        if not self.edit_mode:
            qs = qs.published()
        qs = qs.active_translations(
            translation.get_language()).namespace(self.namespace)
        return qs


class ArticleDetail(PreviewModeMixin, TranslatableSlugMixin, AppConfigMixin, DetailView):
    model = Article
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetail, self).get_context_data(**kwargs)
        context['prev_article'] = self.get_prev_object(self.queryset, self.object)
        context['next_article'] = self.get_next_object(self.queryset, self.object)
        return context

    def get_prev_object(self, queryset=None, object=None):
        if queryset is None:
            queryset = self.get_queryset()
        if object is None:
            object = self.get_object(self)
        prev_objs = queryset.filter(
            publishing_date__lt=object.publishing_date)[:1]
        if prev_objs:
            return prev_objs[0]
        else:
            return None

    def get_next_object(self, queryset=None, object=None):
        if queryset is None:
            queryset = self.get_queryset()
        if object is None:
            object = self.get_object(self)
        next_objs = queryset.filter(
            publishing_date__gt=object.publishing_date)[:1]
        if next_objs:
            return next_objs[0]
        else:
            return None


class ArticleListBase(PreviewModeMixin, ViewUrlMixin, AppConfigMixin, ListView):
    model = Article
    show_header = False

    def get_paginate_by(self, queryset):
        if self.paginate_by is not None:
            return self.paginate_by
        else:
            try:
                return self.config.paginate_by
            except AttributeError:
                return 10  # sensible failsafe


class ArticleList(ArticleListBase):
    """A complete list of articles."""
    show_header = True


class ArticleSearchResultsList(ArticleListBase):
    model = Article
    http_method_names = ['get', 'post', ]
    partial_name = 'aldryn_newsblog/includes/search_results.html'
    template_name = 'aldryn_newsblog/article_list.html'

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('q')
        self.max_articles = request.GET.get('max_articles', 0)
        self.edit_mode = (request.toolbar and request.toolbar.edit_mode)
        return super(ArticleSearchResultsList, self).get(request)

    def get_paginate_by(self, queryset):
        """
        If a max_articles was set (by a plugin), use that figure, else,
        paginate by the app_config's settings.
        """
        return self.max_articles or super(
            ArticleSearchResultsList, self).get_paginate_by(self.get_queryset())

    def get_queryset(self):
        qs = super(ArticleSearchResultsList, self).get_queryset()
        if not self.edit_mode:
            qs = qs.published()
        if self.query:
            return qs.filter(
                Q(translations__title__icontains=self.query) |
                Q(translations__lead_in__icontains=self.query) |
                Q(translations__search_data__icontains=self.query)
            ).distinct()
        else:
            return qs.none()

    def get_context_data(self, **kwargs):
        cxt = super(ArticleSearchResultsList, self).get_context_data(**kwargs)
        cxt['query'] = self.query
        return cxt

    def get_template_names(self):
        if self.request.is_ajax:
            return [self.partial_name, ]
        else:
            return [self.template_name, ]


class AuthorArticleList(ArticleListBase):
    """A list of articles written by a specific author."""
    def get_queryset(self):
        # Note: each Article.author is Person instance with guaranteed
        # presence of unique slug field, which allows to use it in URLs
        return super(AuthorArticleList, self).get_queryset().filter(
            author=self.author
        )

    def get(self, request, author):
        self.author = get_object_or_404(Person, slug=author)
        return super(AuthorArticleList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['newsblog_author'] = self.author
        return super(AuthorArticleList, self).get_context_data(**kwargs)


class CategoryArticleList(ArticleListBase):
    """A list of articles filtered by categories."""
    def get_queryset(self):
        return super(CategoryArticleList, self).get_queryset().filter(
            categories=self.category
        )

    def get(self, request, category):
        self.category = get_object_or_404(
            Category, translations__slug=category)
        return super(CategoryArticleList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['newsblog_category'] = self.category
        ctx = super(CategoryArticleList, self).get_context_data(**kwargs)
        ctx['newsblog_category'] = self.category
        return ctx


class TagArticleList(ArticleListBase):
    """A list of articles filtered by tags."""
    def get_queryset(self):
        return super(TagArticleList, self).get_queryset().filter(
            tags=self.tag
        )

    def get(self, request, tag):
        self.tag = get_object_or_404(Tag, slug=tag)
        return super(TagArticleList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['newsblog_tag'] = self.tag
        return super(TagArticleList, self).get_context_data(**kwargs)


class DateRangeArticleList(ArticleListBase):
    """A list of articles for a specific date range"""
    def get_queryset(self):
        return super(DateRangeArticleList, self).get_queryset().filter(
            publishing_date__gte=self.date_from,
            publishing_date__lt=self.date_to
        )

    def _daterange_from_kwargs(self, kwargs):
        raise NotImplemented('Subclasses of DateRangeArticleList need to'
                             'implement `_daterange_from_kwargs`.')

    def get(self, request, **kwargs):
        self.date_from, self.date_to = self._daterange_from_kwargs(kwargs)
        return super(DateRangeArticleList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['newsblog_day'] = (
            int(self.kwargs.get('day')) if 'day' in self.kwargs else None)
        kwargs['newsblog_month'] = (
            int(self.kwargs.get('month')) if 'month' in self.kwargs else None)
        kwargs['newsblog_year'] = (
            int(self.kwargs.get('year')) if 'year' in self.kwargs else None)
        if kwargs['newsblog_year']:
            kwargs['newsblog_archive_date'] = date(
                kwargs['newsblog_year'],
                kwargs['newsblog_month'] or 1,
                kwargs['newsblog_day'] or 1)
        return super(DateRangeArticleList, self).get_context_data(**kwargs)


class YearArticleList(DateRangeArticleList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), 1, 1)
        date_to = date_from + relativedelta(years=1)
        return date_from, date_to


class MonthArticleList(DateRangeArticleList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), int(kwargs['month']), 1)
        date_to = date_from + relativedelta(months=1)
        return date_from, date_to


class DayArticleList(DateRangeArticleList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(
            int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        date_to = date_from + relativedelta(days=1)
        return date_from, date_to
