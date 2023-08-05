import json
import os
from flask import jsonify, request
from jobmanager.models import Job, purge_completed_jobs
from . import app, with_db_session


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/job_stats/")
@with_db_session
def get_job_statistics(session):
    q = session.query(Job).filter(Job.finished == None).filter(Job.submitted == None)
    jobs_waiting = len([_ for _ in q.all()])
    q = session.query(Job).filter(Job.finished == None).filter(Job.submitted != None)
    jobs_running = len([_ for _ in q.all()])
    return jsonify({'waiting': jobs_waiting, 'running': jobs_running})


@app.route("/jobs/<job_id>/results", methods=['GET'])
@with_db_session
def get_job_results(session, job_id):
    job = session.query(Job).filter_by(job_id=job_id).first()
    results = {}
    try:
        data = json.loads(job.results).get('map', {}).get('entry', [])
        for d in data:
            if 'string' in d:
                values = d['string']
                if len(values) == 2:
                    results[values[0]] = values[1]
    except:
        pass
    results['job_id'] = job.job_id
    results['state'] = job.state
    return jsonify(results)


@app.route("/jobs/<job_id>", methods=['GET'])
@with_db_session
def get_job(session, job_id):
    return jsonify(session.query(Job).filter_by(job_id=job_id).first().to_dict())


@app.route("/jobs/", methods=['GET'])
@with_db_session
def jobs(session):
    active_only = request.args.get('active')
    query = session.query(Job)
    if active_only:
        query = query.filter(Job.finished == None)
    return json.dumps([job.to_dict() for job in query.all()])


@app.route("/jobs/", methods=['DELETE'])
@with_db_session
def purge_jobs(session):
    purge_completed_jobs(session)
    return jsonify({'result': True})


@app.route('/system_info/', methods=['GET'])
def system_info():
    params = app.config.get('params', {})
    dialect = params.get('database_dialect')
    if not params or not dialect:
        return jsonify({'result': False, 'error_string': 'config parameters missing'})

    info = {}
    if dialect == 'sqlite':
        db_size = os.path.getsize(app.config['params']['database_connect_string'])
        info['db_size'] = db_size / 1000

    else:
        return jsonify({'result': False, 'error_string': 'unknown database dialect'})

    info['result'] = True
    return jsonify(info)
