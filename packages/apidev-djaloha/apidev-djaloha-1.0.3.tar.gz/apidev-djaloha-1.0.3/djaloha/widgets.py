# -*- coding: utf-8 -*-
"""widgets to be used in a form"""

from django.forms import Media

from floppyforms.widgets import TextInput

from djaloha import settings


class AlohaInput(TextInput):
    """
    Text widget with aloha html editor
    requires floppyforms to be installed
    """

    template_name = 'djaloha/alohainput.html'

    def __init__(self, *args, **kwargs):
        # for compatibility with previous versions
        kwargs.pop('text_color_plugin', None)

        self.aloha_plugins = kwargs.pop('aloha_plugins', None)
        self.extra_aloha_plugins = kwargs.pop('extra_aloha_plugins', None)
        self.aloha_init_url = kwargs.pop('aloha_init_url', None)
        super(AlohaInput, self).__init__(*args, **kwargs)

    def _get_media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        """

        try:
            aloha_init_url = self.aloha_init_url or settings.init_url()
            aloha_version = settings.aloha_version()

            aloha_plugins = self.aloha_plugins
            if not aloha_plugins:
                aloha_plugins = settings.plugins()

            if self.extra_aloha_plugins:
                aloha_plugins = tuple(aloha_plugins) + tuple(self.extra_aloha_plugins)

            css = {
                'all': (
                    "{0}/css/aloha.css".format(aloha_version),
                )
            }

            javascripts = []

            if not settings.skip_jquery():
                javascripts.append(settings.jquery_version())

            #if aloha_version.startswith('aloha.0.22.') or aloha_version.startswith('aloha.0.23.'):
            javascripts.append("{0}/lib/require.js".format(aloha_version))

            javascripts.append(aloha_init_url)
            javascripts.append(
                u'{0}/lib/aloha.js" data-aloha-plugins="{1}'.format(aloha_version, u",".join(aloha_plugins))
            )
            javascripts.append('djaloha/js/djaloha-init.js')
            
            return Media(css=css, js=javascripts)
        except Exception, msg:
            print '## AlohaInput._get_media Error ', msg

    media = property(_get_media)
