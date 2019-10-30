from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination

from jobs.models import Job
from jobs.serializers import JobSerializer


class ElasticsearchPagination(LimitOffsetPagination):

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


class JobElasticListView(ListCreateAPIView):
    queryset = Job.objects.all()
    http_method_names = ['get', ]
    pagination_class = ElasticsearchPagination
    serializer_class = JobSerializer


class JobDatabaseListAPIView(ListCreateAPIView):
    queryset = Job.objects.all()
    http_method_names = ['get', ]
    serializer_class = JobSerializer
