# -*- coding: utf-8 -*-
"""Forms for SAM module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django_search_forms.form import SearchForm
from django_search_forms.fields import SearchField

from ralph.middleware import get_actual_regions


class RegionRelatedSearchField(SearchField, forms.ChoiceField):
    """A field that allows to search region."""

    def __init__(self, Model, *args, **kwargs):
        kwargs['choices'] = [('', '----')]
        super(RegionRelatedSearchField, self).__init__(*args, **kwargs)

    def get_query(self, value):
        self.region = 'region'
        return Q(**{self.name + '__id': int(value)})


class RegionSearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(RegionSearchForm, self).__init__(*args, **kwargs)
        self.fields['region'].choices = [('', '----')] + [
            (unicode(object_.id), unicode(object_))
            for object_ in get_actual_regions()
        ]
