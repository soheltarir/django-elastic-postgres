from csv import DictReader

from django.db import transaction

from jobs.models import Company, Job


@transaction.atomic
def run():
    csvfile = open('seed_job_data.csv', mode='r', encoding="utf-8-sig")
    reader = DictReader(csvfile)
    for row in reader:
        try:
            try:
                company = Company.objects.get(name=row['company_name'])
            except Company.DoesNotExist:
                company = Company.objects.create(name=row['company_name'], website=row['company_website'])
            job = Job.objects.create(
                title=row['title'],
                company=company,
                vacancies=row['vacancies'],
                salary=row['salary']
            )
            print('Created Test Job with Title {}'.format(job))
        except Exception:
            pass
