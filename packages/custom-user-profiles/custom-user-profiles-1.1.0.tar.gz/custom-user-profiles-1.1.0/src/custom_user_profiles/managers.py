#!/usr/bin/env python
# encoding: utf-8
from django.db.models import query
from model_utils.managers import PassThroughManager


class QuerySetManager(query.QuerySet):
    @classmethod
    def manager(cls):
        return PassThroughManager.for_queryset_class(cls)()


class CustomUserQuerySet(QuerySetManager):
    def __getattr__(self, name):
        def wrapper():
            lookup = '%s__isnull' % name
            return self.filter(**{lookup: False})
        return wrapper
