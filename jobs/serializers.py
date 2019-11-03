from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from jobs.models import Job, Company


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'website')


class JobSerializer(ModelSerializer):
    company = CompanySerializer(read_only=True)
    company_id = PrimaryKeyRelatedField(queryset=Company.objects, write_only=True, required=True)

    class Meta:
        model = Job
        fields = ('id', 'title', 'company', 'vacancies', 'salary', 'company_id')

    def create(self, validated_data):
        validated_data['company'] = validated_data.pop('company_id')
        return super().create(validated_data)
