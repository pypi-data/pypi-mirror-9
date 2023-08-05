# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import get_language

from parler.managers import TranslatableManager


class RelatedManager(TranslatableManager):

    def filter_by_language(self, language):
        return self.active_translations(language)

    def filter_by_current_language(self):
        return self.filter_by_language(get_language())


class CategoryManager(TranslatableManager):

    def get_categories(self, language=None):
        categories = self.active_translations(language).prefetch_related('questions')

        for category in categories:
            category.count = (category.questions
            .filter_by_language(language).count())
        return sorted(categories, key=lambda x: -x.count)
