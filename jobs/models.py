from django.conf import settings
from django.db import models

from jobs.managers import BaseManager


class ElasticModelMixin(models.Model):
    class Meta:
        abstract = True
        app_label = 'jobs'

    @classmethod
    def elastic_index(cls):
        return settings.ELASTIC_CONSTANTS[cls.__name__]['index']

    @classmethod
    def elastic_type(cls):
        return settings.ELASTIC_CONSTANTS[cls.__name__]['doc_type']


class Company(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    website = models.URLField(max_length=255, null=True)

    class Meta:
        app_label = 'jobs'
        db_table = 'companies'


class Job(ElasticModelMixin):
    title = models.CharField(max_length=255, null=False, blank=False)
    company = models.ForeignKey('jobs.Company', null=False, on_delete=models.CASCADE)
    vacancies = models.PositiveSmallIntegerField(null=False)
    salary = models.PositiveIntegerField(null=False)

    objects = BaseManager()

    class Meta:
        app_label = "jobs"
        db_table = "jobs"

    def __str__(self):
        return self.title
