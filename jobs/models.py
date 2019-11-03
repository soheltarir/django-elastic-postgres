from django.conf import settings
from django.db import models, connection
from elasticsearch import Elasticsearch

from jobs.managers import BaseManager


class ElasticModelMixin(models.Model):
    class Meta:
        abstract = True
        app_label = 'jobs'

    @classmethod
    def elastic_index(cls):
        """
        :return: Elasticsearch index name / alias of the model
        """
        return settings.ELASTIC_CONSTANTS[cls.__name__]['index']

    @classmethod
    def elastic_type(cls):
        """
        :return: Elasticsearch document type of the model
        """
        return settings.ELASTIC_CONSTANTS[cls.__name__]['doc_type']

    @property
    def pg_data(self):
        """
        Retrieves data by executing the Postgres Functions
        :return: Object
        """
        _pg_func = settings.ELASTIC_CONSTANTS[self.__class__.__name__]['pg_function']
        query = "SELECT {}({})".format(_pg_func, self.id)
        cursor = connection.cursor()
        cursor.execute(query)
        res = cursor.fetchone()
        return res[0]

    def index_to_elastic(self):
        """
        Indexes the instance data in elasticsearch
        :raises TransportError if the indexing fails
        """
        es_client = Elasticsearch(settings.ELASTIC_HOST)
        es_client.index(index=self.elastic_index(), doc_type=self.elastic_type(), id=str(self.id), body=self.pg_data)

    def from_elastic(self):
        """
        Fetches the instance document from Elasticsearch
        :return: Instance data in Dict
        :raises ElasticNotFound if the document is not found in elasticsearch
        """
        es_client = Elasticsearch(settings.ELASTIC_HOST)
        es_res = es_client.get(index=self.elastic_index(), doc_type=self.elastic_type(), id=str(self.id))
        return es_res['_source']


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
