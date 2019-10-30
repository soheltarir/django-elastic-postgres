import json

from django.db import connection
from elasticsearch import Elasticsearch

from jobs.models import Job

es_client = Elasticsearch('http://localhost:9200')


def run():
    # Create Index
    es_client.indices.create(index='jobs')

    # Put Mapping
    with open("jobs/job.json", "r") as fp:
        es_client.indices.put_mapping(index='jobs', doc_type='job', body=json.load(fp))

    # Start Indexing
    job_ids = Job.objects.values_list('id', flat=True)
    db_cursor = connection.cursor()
    for job_id in job_ids:
        query = "SELECT get_job_data({});".format(job_id)
        db_cursor.execute(query)
        result = db_cursor.fetchone()
        es_client.index(index='jobs', doc_type='job', body=result[0])
        print("Indexed job {}".format(job_id))
