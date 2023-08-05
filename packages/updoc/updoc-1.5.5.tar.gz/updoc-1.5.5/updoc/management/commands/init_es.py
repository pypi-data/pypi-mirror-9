#coding=utf-8
import json
from django.core.management import BaseCommand
import subprocess
from updoc.indexation import create_index, index_archive
from updoc.models import UploadDoc
from updoc.progress.progressbar import ProgressBar
from updoc.progress.widgets import Bar, Percentage

__author__ = 'flanker'


class ImportProgressBar(ProgressBar):

    def __init__(self, model):
        print('Indexing %s...' % model.__name__)
        super(ImportProgressBar, self).__init__(widgets=[Percentage(), Bar()], maxval=model.objects.count())
        self.__pb_value = 0
        self.start()

    def add(self):
        self.__pb_value += 1
        if self.__pb_value >= self.maxval or self.__pb_value % 10 == 0:
            super(ImportProgressBar, self).update(self.__pb_value)


class Command(BaseCommand):
    """Print basic configuration files for different kinds of deployment"""
    # pylint: disable=R0912
    # pylint: disable=R0915
    args = ''
    help = 'Initialize ElasticSearch index'

    def handle(self, *args, **options):
        queries = create_index()
        for query in queries:
            print(query)
            stdout = subprocess.check_output(query, shell=True, stderr=subprocess.PIPE)
            message = json.loads(stdout.decode('utf-8'))
            if message.get('status', 200) >= 300:
                print(message.get('error'))
            else:
                print('ok')
        pb = ImportProgressBar(UploadDoc)
        for updoc in UploadDoc.objects.all():
            index_archive(updoc.id, updoc.path)
            pb.add()
        pb.finish()


if __name__ == '__main__':
    import doctest

    doctest.testmod()