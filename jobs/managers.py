from django.db.models import QuerySet, Manager
from elasticsearch import Elasticsearch


class BaseQuerySet(QuerySet):
    def elastic_list(self, query=None):
        if query is None:
            query = {}
        es_client = Elasticsearch('http://localhost:9200')
        res = es_client.search(index=self.model.elastic_index(), doc_type=self.model.elastic_type(), body=query)
        # Clean data
        _hits = res["hits"]["hits"]
        hits = []
        for _hit in _hits:
            hits.append(_hit['_source'])
        return res['hits']['total'], hits


class BaseManager(Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)

    def elastic_list(self):
        return self.get_queryset().elastic_list()
