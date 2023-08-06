# coding: utf-8
# сeated on 18 дек. 2014 г.
# author: Michael Vorotyntsev

from architect.orms.django.mixins import PartitionableMixin
from datalogging.models import DataLog
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    u"""
    Используется вместо
    $export DJANGO_SETTINGS_MODULE=mysite.settings
    $architect partition --module path.to.the.model.module
    у которого есть проблемы с импортом settings,
    проще написать:
    $python manage.py datalogging_partition_prepare

    """

    help = u'Architect table partition setup'

    def handle(self, *args, **options):
        empty_record = DataLog()
        if isinstance(empty_record, PartitionableMixin):
            empty_record.get_partition().prepare()
