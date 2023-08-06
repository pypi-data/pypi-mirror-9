import django

from django.db.models.query import QuerySet as BaseQuerySet
from django.db import models


class QuerySet(BaseQuerySet):
    def first(self):
        """
        Returns the first object of a query, returns None if no match is found.
        """
        qs = self if self.ordered else self.order_by('pk')
        try:
            return qs[0]
        except IndexError:
            return None

    def last(self):
        """
        Returns the last object of a query, returns None if no match is found.
        """
        qs = self.reverse() if self.ordered else self.order_by('-pk')
        try:
            return qs[0]
        except IndexError:
            return None


class Manager(models.Manager):
    def get_queryset(self):
        return QuerySet(self.model)

    if django.VERSION < (1, 6):
        get_query_set = get_queryset

    def first(self):
        return self.get_queryset().first()

    def last(self):
        return self.get_queryset().last()
