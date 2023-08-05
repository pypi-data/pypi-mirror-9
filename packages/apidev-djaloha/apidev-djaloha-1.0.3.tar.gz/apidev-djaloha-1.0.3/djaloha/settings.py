# -*- coding: utf-8 -*-
"""centralize settings"""

from django.conf import settings as project_settings
from django.core.urlresolvers import reverse


def aloha_version():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_ALOHA_VERSION', "aloha.0.23.26")


def init_js_template():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_INIT_JS_TEMPLATE', "djaloha/aloha_init.js")


def init_url():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_INIT_URL', None) or reverse('aloha_init')


def plugins():
    """return settings or default"""
    plugins_ = getattr(project_settings, 'DJALOHA_PLUGINS', None)
    if not plugins_:
        plugins_ = (
            "common/format",
            #"custom/format",
            "common/highlighteditables",
            "common/list",
            "common/link",
            "common/undo",
            "common/paste",
            "common/commands",
            "common/contenthandler",
            "common/image",
            #"custom/zimage",
            "common/align",
            #"extra/attributes",
            "common/characterpicker",
            #"common/abbr",
            "common/horizontalruler",
            #"common/table",
            #"extra/metaview",
            #"extra/textcolor",
        )
    return plugins_


def skip_jquery():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_SKIP_JQUERY', False)
    

def jquery_version():
    """return settings or default"""
    if project_settings.DEBUG:
        return getattr(project_settings, 'DJALOHA_JQUERY', "js/jquery-1.7.2.js")
    else:
        return getattr(project_settings, 'DJALOHA_JQUERY', "js/jquery-1.7.2.js")
    

def jquery_no_conflict():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_JQUERY_NO_CONFLICT', True)
    

def link_models():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_LINK_MODELS', ())
    

def sidebar_disabled():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_SIDEBAR_DISABLED', True)
    

def css_classes():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_CSS_CLASSES', ())
    

def resize_disabled():
    """return settings or default"""
    return getattr(project_settings, 'DJALOHA_RESIZE_DISABLED', False)
