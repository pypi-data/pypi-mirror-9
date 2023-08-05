# -*- coding: utf-8 -*-
from .conf import settings
import django.template.loaders.app_directories
from django.utils._os import safe_join


_cache = None


def clear_cache():
    global _cache
    _cache = None


def _populate_cache():
    global _cache
    _cache = tuple([
        safe_join(
            '{}{}'.format(template_dir, '_for_boilerplates'),
            settings.ALDRYN_BOILERPLATE_NAME,
        )
        for template_dir
        in django.template.loaders.app_directories.app_template_dirs
    ])


def _get_boilerplate_app_template_dirs(template_dirs):
    if template_dirs is not None:
        return template_dirs
    if _cache is None:
        _populate_cache()
    return _cache


class AppDirectoriesLoader(django.template.loaders.app_directories.Loader):
    is_usable = settings.ALDRYN_BOILERPLATE_NAME is not None

    def get_template_sources(self, template_name, template_dirs=None):
        return super(AppDirectoriesLoader, self).get_template_sources(
            template_name,
            _get_boilerplate_app_template_dirs(template_dirs),
        )

    def load_template_source(self, template_name, template_dirs=None):
        return super(AppDirectoriesLoader, self).load_template_source(
            template_name,
            _get_boilerplate_app_template_dirs(template_dirs),
        )
