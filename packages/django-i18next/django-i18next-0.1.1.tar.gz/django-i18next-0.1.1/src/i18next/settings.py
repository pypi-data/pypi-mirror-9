"""
- `DEBUG`
"""
__title__ = 'i18next.settings'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DEBUG',)

from i18next.conf import get_setting

DEBUG = get_setting('DEBUG')
