from rest_framework.serializers import ModelSerializer

from jobs.models import Job, Company


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'website')


class JobSerializer(ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Job
        fields = ('id', 'title', 'company', 'vacancies', 'salary')
