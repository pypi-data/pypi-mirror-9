# coding=utf-8
from io import StringIO
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import ugettext as _


__author__ = 'flanker'


class Command(BaseCommand):

    def handle(self, *args, **options):
        conf = settings.CONFIGURATION
        print(_('Read .ini configuration files: '))
        print(', '.join(conf.read_filenames))
        print('')
        print(_('Content of the configuration, including default values:'))
        v = StringIO()
        conf.write(v)
        print(v.getvalue())


if __name__ == '__main__':
    import doctest

    doctest.testmod()