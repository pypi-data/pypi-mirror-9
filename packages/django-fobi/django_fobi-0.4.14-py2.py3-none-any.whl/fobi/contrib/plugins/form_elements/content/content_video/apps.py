__title__ = 'fobi.contrib.plugins.form_elements.content.content_video.apps'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('Config',)

try:
    from django.apps import AppConfig

    class Config(AppConfig):
        name = label = 'fobi.contrib.plugins.form_elements.content.content_video'

except ImportError:
    pass
