from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from jobs.models import Job
from jobs.serializers import JobSerializer


class ElasticsearchPagination(LimitOffsetPagination):
    def __init__(self):
        super().__init__()
        self.limit, self.offset = 10, 0
        self.count = 0
        self.request = None

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        es_query = {
            "size": self.limit,
            "from": self.limit
        }
        self.count, data = queryset.elastic_list(query=es_query)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return data


class ElasticListCreateAPIView(ListCreateAPIView):
    pagination_class = ElasticsearchPagination

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        return self.get_paginated_response(page)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Insert in database
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # Fetch data from PostgreSQL function and index to Elasticsearch
        instance.index_to_elastic()
        # Fetch the created data from elasticsearch
        return Response(instance.from_elastic(), status=status.HTTP_201_CREATED)


class JobElasticListView(ElasticListCreateAPIView):
    queryset = Job.objects.all()
    http_method_names = ['get', 'post']
    serializer_class = JobSerializer


class JobDatabaseListAPIView(ListCreateAPIView):
    queryset = Job.objects.all()
    http_method_names = ['get', 'post']
    serializer_class = JobSerializer
