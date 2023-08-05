# encoding: utf-8

from django.db import models

from django_random_queryset import strategies


class RandomQuerySet(models.query.QuerySet):

    def __init__(self, *args, **kwargs):

        try:
            self._strategy = kwargs.pop('strategy')

        except KeyError:
            self._strategy = strategies.DEFAULT

        super(RandomQuerySet, self).__init__(*args, **kwargs)

    def random(self, amount=1):
        return self.filter(id__in=self._strategy(
            amount,
            self.values_list('id', flat=True)))

