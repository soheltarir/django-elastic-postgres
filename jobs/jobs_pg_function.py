from django.db import connection

pg_function = """
CREATE OR REPLACE FUNCTION get_job_data(job_id INTEGER )
  RETURNS JSONB AS
$BODY$
DECLARE 
    job_data JSONB;
BEGIN
    SELECT 
        jsonb_build_object(
            'id', j.id,
            'title', j.title,
            'vacancies', j.vacancies,
            'salary', j.salary,
            'company', jsonb_build_object(
                'id', c.id,
                'name', c.name,
                'website', c.website
            )
        ) INTO job_data
    FROM jobs j 
    INNER JOIN companies c on j.company_id = c.id
    WHERE j.id = $1;
    RETURN job_data;
END 
$BODY$
LANGUAGE plpgsql IMMUTABLE
COST 100;

"""


def list_jobs(limit=20, offset=0):
    cursor = connection.cursor()
    query = """
    SELECT json_agg(data.json_data) FROM (SELECT get_job_data(job.id) AS json_data 
    FROM employer_job job OFFSET {} LIMIT {}) data;
    """.format(offset, limit)
    cursor.execute(query)
    result = cursor.fetchone()
    if not result[0]:
        return []
    return result[0]
