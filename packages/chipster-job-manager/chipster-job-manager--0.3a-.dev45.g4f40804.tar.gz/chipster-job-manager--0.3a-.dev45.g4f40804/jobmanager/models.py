from __future__ import unicode_literals
import datetime
import logging
from sqlalchemy import (Column, Integer, String, Text,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base

from jobmanager.utils import parse_description

Base = declarative_base()


class JobNotFound(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = 'job %s does not exists' % message


class Job(Base):
    __tablename__ = 'jobs'
    __publicfields__ = ['job_id', 'description', 'headers', 'results', 'created',
                        'rescheduled', 'submitted', 'finished', 'seen', 'retries',
                        'comp_id', 'state']

    id = Column(Integer, primary_key=True)
    job_id = Column(String(length=40))
    session_id = Column(String(length=40))
    description = Column(Text)
    headers = Column(Text)
    results = Column(Text)
    analysis_id = Column(Text)
    reply_to = Column(String(length=255))
    state = Column(String(length=32))
    created = Column(DateTime)
    rescheduled = Column(DateTime)
    submitted = Column(DateTime)
    username = Column(String(255))
    finished = Column(DateTime)
    seen = Column(DateTime)
    retries = Column(Integer, default=0)
    comp_id = Column(String(length=40))

    def to_dict(self):
        d = {}
        for k in self.__publicfields__:
            d[k] = getattr(self, k)
            if k in ('description'):
                description = parse_description(self.description)
                d['analysis_id'] = description.get('analysisID')
            elif k in ('created', 'submitted', 'finished', 'seen', 'rescheduled'):
                if d[k]:
                    try:
                        d[k] = d[k].strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                    if k in ('submitted'):
                        try:
                            d['queuing_time'] = (self.submitted - self.created).total_seconds()
                        except:
                            pass
                    if k in ('finished'):
                        try:
                            d['execution_time'] = (self.finished - self.submitted).total_seconds()
                        except:
                            pass
        return d

    def __unicode__(self):
        return '<Job:%s>' % self.job_id

    def __str__(self):
        return self.__unicode__()


def get_jobs(session, include_finished=False):
    if include_finished:
        return session.query(Job).all()
    else:
        return session.query(Job).filter(Job.finished == None)


def get_job(session, job_id):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)
    return job


def add_job(session, job_id, description, headers, session_id, reply_to=None):
    desc = {}
    desc['job_id'] = job_id
    desc['description'] = description
    parsed_description = parse_description(description)
    desc['analysis_id'] = parsed_description.get('analysisID')
    desc['created'] = datetime.datetime.utcnow()
    desc['headers'] = headers
    desc['state'] = 'NEW'
    desc['reply_to'] = reply_to
    desc['session_id'] = session_id
    job = Job(**desc)
    session.add(job)
    return job


def update_job_comp(session, job_id, comp_id):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)
    if job.results:
        raise ValueError('cannot modify finished job: %s' % job_id)
    job.submitted = datetime.datetime.utcnow()
    job.state = 'SUBMITTED'
    job.comp_id = comp_id
    session.merge(job)
    return job


def update_job_reply_to(session, job_id, reply_to):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)
    job.reply_to = reply_to
    session.merge(job)
    return job


def update_job_results(session, job_id, results, exit_state):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)

    if not job.comp_id:
        logging.warn('addings results to job %s with no comp_id' % job_id)
    job.finished = datetime.datetime.utcnow()
    job.state = exit_state
    job.results = results.decode("utf8")
    session.merge(job)
    return job


def update_job_running(session, job_id):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)
    job.seen = datetime.datetime.utcnow()
    job.state = 'RUNNING'
    session.merge(job)
    return job


def update_job_rescheduled(session, job_id):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)
    if job.finished:
        raise RuntimeError("cannot reschedule finished job")
    now = datetime.datetime.utcnow()
    job.rescheduled = now
    job.submitted = now
    job.retries = job.retries + 1
    job.state = 'RESCHEDULED'
    job.seen = None
    session.merge(job)
    return job


def update_job_cancelled(session, job_id):
    job = session.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise JobNotFound(job_id)
    if job.finished:
        raise RuntimeError("cannot cancel completed job")
    job.finished = datetime.datetime.utcnow()
    job.state = 'CANCELLED'
    session.merge(job)
    return job


def purge_completed_jobs(session, months=3):
    if type(months) is not int:
        raise ValueError("months parameter must have integer type")
    if months <= 1:
        raise RuntimeError("months parameter must be greater than one")
    delta = datetime.timedelta(30 * months)
    now = datetime.datetime.utcnow()
    jobs = session.query(Job).filter(Job.finished < (now - delta))
    for job in jobs:
        session.delete(job)
