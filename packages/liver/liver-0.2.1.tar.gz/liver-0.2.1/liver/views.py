# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from models import *

import datetime, time, pytz
import simplejson as json
import urlparse
import os

from functools import wraps

import logging
logger = logging.getLogger("liver.views")

import warnings
warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

################################################################################


def get_parameter(request, name):
    if request.POST:
        try:
          return request.POST[name]
        except KeyError:
          pass
    if request.GET:
        try:
          return request.GET[name]
        except KeyError as e:
          raise e

def get_token(func):
    def inner_decorator(request, *args, **kwargs):
        try:
          token = get_parameter(request, "token")
        except Exception,e:
          logger.warning("Token was not received")
          token = None
        request.token=token
        return func(request, *args, **kwargs)
    return wraps(func)(inner_decorator)


def json_response(res):
    json_responses = json.dumps(res)
    logger.debug('Query result: %s' % str(json_responses))
    return HttpResponse(json_responses,
        mimetype='application/json')


def return_error(error_code, error_message=None):
    if not error_message:
        if error_code == -500:
            error_message = "Internal Server Error"
        elif error_code == -400:
            error_message = "Bad request"
        elif error_code == -401:
            error_message = "Unauthorized"
        elif error_code == -403:
            error_message = "Forbidden"
        elif error_code == -404:
            error_message = "Not Found"
        elif error_code == -450:
            error_message = "Resource busy"
        else:
            error_message = "Unknown error"

    return (error_code, error_message)

################################################################################


@get_token
@transaction.atomic
def api_external_get_worker_job(request):
    res = {
      "result": 0,
      "response": ""
    }

    token = request.token

    try:
      start_before = get_parameter(request, "start_before")
      start_before_date = \
          datetime.datetime.fromtimestamp(long(start_before), pytz.UTC)
    except Exception:
      start_before_date = \
          datetime.datetime.fromtimestamp(time.time()+300, pytz.UTC)

    logger.debug("start_before_date: %s" % start_before_date)

    try:
      start_after = get_parameter(request, "start_after")
      start_after_date = \
          datetime.datetime.fromtimestamp(long(start_after), pytz.UTC)
    except Exception:
      start_after_date = \
          datetime.datetime.fromtimestamp(time.time()-300, pytz.UTC)

    logger.debug("start_after_date: %s" % start_after_date)

    try:
        recorder = \
            Recorder.objects.filter(token=token)[0]
    except Exception:
        logger.error("No recorder associated to this token: %s" % token)
        result,response = return_error(-403)
        res["result"]=result
        res["response"]=response
        return json_response(res)

    try:
        job_list = RecordingJob.objects\
                .filter(enabled=True)\
                .filter(status="waiting")\
                .filter(scheduled_start_date__lte=start_before_date)\
                .filter(scheduled_start_date__gte=start_after_date)\
                .order_by("-scheduled_start_date")
        try:
            job = job_list[0]
            job.recorder = recorder
            job.status = "running"
            job.execution_date = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            job.save()
        except Exception:
          res["result"] = -2
          res["response"] = "There is not available jobs"
          return json_response(res)

        job_dict = {}
        job_dict["id"] = job.id
        job_dict["start"] = job.scheduled_start_timestamp
        job_dict["duration"] = job.scheduled_duration
        job_dict["smil"] = job.slug() + ".smil"
        job_dict["profiles"] = []

        sg = job.sources_group
        job_dict["name"] = sg.name
        for s in sg.source_set.all():
            profile_dict = {}
            profile_dict["id"]=s.id
            profile_dict["uri"]=s.uri
            profile_dict["bitrate"]=s.bitrate
            profile_dict["name"]=\
job.slug() + "_" + str(s.id) + "_" + str(s.bitrate) + ".mp4"
            job_dict["profiles"].append(profile_dict)

        response = job_dict
        res["response"] = response
        return json_response(res)

    except IOError, e:
        res["result"] = -99
        res["response"] = "Unexpected error: %s" % str(e)
        return json_response(res)

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

@csrf_exempt
@get_token
@transaction.commit_on_success
def api_external_notify_worker_job_result(request):

    submitted_jobs_result = request.body
    logger.debug("worker jobs result received: %s" % submitted_jobs_result)

    try:
      job_result_dict = json.loads(submitted_jobs_result)
    except ValueError:
        res = {}
        c,m = return_error (-400)
        res["result"] = c
        res["response"] = m
        return json_response(res)

    # >>> d['job'].keys()
    # ['name','duration', 'start', 'id', 'profiles', 'result']
    # >>> d['job']['profiles'][0].keys()
    # ['job_start', 'job_duration', 'name', 'duration', 'id', 'destination', 'uri', 'job_id', 'result']

    job_dict= job_result_dict["job"]
    try:
            job = RecordingJob.objects.get(id=job_dict["id"],
                recorder__token=request.token)
            job.completion_date = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            job.result=job_result_dict["log"][:50000]
            if job_dict['result'] != 0:
                job.status="failed"
                logger.error("Recording job %s failed" % (job))
                job.save()
            else:
                job.status="successful"
                job.save()

                r = Recording()
                r.recording_job=job
                r.recorder=job.recorder
                r.name="%(name)s-%(start)s-%(duration)s" % (job_dict)
                r.profiles_json=json.dumps(job_dict['profiles'])
                metadata_list = []
                for m in job.recordingjobmetadata_set.all():
                    metadata_list.append({m.key:m.value})
                metadata_list.append({"start_date":str(job.scheduled_start_date)})
                metadata_list.append({"start_timestamp":job.scheduled_start_timestamp})
                metadata_list.append({"duration":job.scheduled_duration})
                metadata_list.append({"smil":job_dict["smil"]})

                r.metadata_json=json.dumps(metadata_list)
                r.save()

    except ObjectDoesNotExist:
            logger.error("Job id %s doesn't exist" % (job_dict["id"]))
    except MultipleObjectsReturned:
            logger.error("Multiple selectables objects with id %s" % (job_dict["id"]))
    except Exception  as e:
            logger.error("Unexpected exception saving a job result: %s" % (e))


    res = {
            "result": 0,
            "response": "Job status updated"
    }
    return json_response(res)


@get_token
@transaction.commit_on_success
def api_external_get_mo_to_delete(request):
    try:
        res = {
          "result": 0,
          "response": ""
        }

        token = request.token

        try:
            recorder = \
                Recorder.objects.filter(token=token)[0]
        except Exception:
            logger.error("No recorder associated to this token: %s" % token)
            result,response = return_error(-403)
            res["result"]=result
            res["response"]=response
            return json_response(res)

        recordings_to_delete_list = Recording.objects\
            .filter(to_delete=True).iterator()

        response = []
        for r in recordings_to_delete_list:
            try:
                logger.info("Deleting recording %s" % (r))

                profiles = json.loads(r.profiles_json)
                logger.debug("Deleting profiles for %s : %s" % (r,r.profiles_json))
                dirname = "."
                for p in profiles:
                    dirname = os.path.dirname(p["destination"])
                    response.append(p["destination"])

                metadata = json.loads(r.metadata_json)
                for m in metadata:
                    if m.has_key("smil"):
                        smil = dirname + "/" + m["smil"]
                        logger.debug("Deleting smil for %s : %s" % (r,smil))
                        response.append(smil)

                logger.info("Deleting recording %s" % (r))
                logger.debug("Deleting profiles for %s : %s" % (r,r.profiles_json))
                for p in profiles:
                    response.append(p["destination"])
                r.delete()
            except Exception as e:
                logger.error( "Exception occurs getting profiles for %s: %s"% (r,e))
        res["response"]=response
        return json_response(res)

    except Exception as e:
      res["result"] = -9
      res["response"] = "Unexpected error: %s" % str(e)
      return json_response(res)


@get_token
@transaction.commit_on_success
def api_external_get_mo(request):
    try:
        res = {
          "result": 0,
          "response": ""
        }

        token = request.token

        all_mo = 0
        try:
            all_mo = get_parameter(request, "all")
            all_mo = int(all_mo)
        except Exception:
            pass

        try:
            recorder = \
                Recorder.objects.filter(token=token)[0]
        except Exception:
            logger.error("No recorder associated to this token: %s" % token)
            result,response = return_error(-403)
            res["result"]=result
            res["response"]=response
            return json_response(res)



        if all_mo == 1:
            recordings_list = Recording.objects.iterator()
        else:
            recordings_list = Recording.objects\
                .filter(to_delete=False).iterator()

        response = []
        for r in recordings_list:
            try:
                profiles = json.loads(r.profiles_json)
                logger.debug("Getting profiles for %s : %s" % (r,r.profiles_json))
                for p in profiles:
                    response.append(p["destination"])
                metadatas = json.loads(r.metadata_json)
                if all_mo == 1:
                    logger.debug("Getting smil for %s : %s" % (r,r.metadata_json))
                    for m in metadatas:
                        try:
                            k = m.keys()[0]
                            v = m.values()[0]
                            if k == "smil":
                                response.append(v)
                        except Exception,e:
                            logger.critical(e)
                            pass

            except Exception as e:
                logger.error( "Exception occurs getting profiles for %s: %s"% (r,e))
        res["response"]=response
        return json_response(res)

    except Exception as e:
      res["result"] = -9
      res["response"] = "Unexpected error: %s" % str(e)
      return json_response(res)

@csrf_exempt
@get_token
@transaction.commit_on_success
def api_external_update_recordings(request):
    try:
        res = {
          "result": 0,
          "response": ""
        }

        token = request.token

        now = int(time.time())
        now_date = datetime.datetime.fromtimestamp(now,pytz.UTC)

        try:
            application = Application.objects.filter(token=token)\
                 .filter(valid=True)\
                 .filter( Q(valid_since__lt=now_date)\
                                        | Q(valid_since__isnull=True) ) \
                 .filter( Q(valid_until__gt=now_date)\
                                        | Q(valid_until__isnull=True) )[0]

        except Exception, e:
            logger.debug("Exception getting application: %s", e)
            logger.error("No application associated to this token: %s" % token)
            result,response = return_error(-403)
            res["result"]=result
            res["response"]=response
            return json_response(res)

        submitted_updatings = request.body
        logger.debug("update_recordings received: %s" % submitted_updatings)

        try:
            updatings = json.loads(submitted_updatings)
        except ValueError:
            res = {}
            c,m = return_error (-400)
            res["result"] = c
            res["response"] = m
            return json_response(res)

        for u in updatings:
            updating_problem=True
            logger.info("Request for updating recordings: %s" % u)
            recordings = None
            if u.has_key("database_key"):
                recordings = Recording.objects.filter(\
metadata_json__contains='{"database_key": "%s"}'%u["database_key"].strip())
            else:
                if u.has_key("event_id"):
                    recordings = Recording.objects.filter(\
metadata_json__contains='{"event_id": "%s"}'%u["event_id"].strip())

            recording_jobs = []
            if u.has_key("database_key"):
                r_j_m_list = RecordingJobMetadata.objects.filter(\
key="database_key",value=u["database_key"].strip()).iterator()
                for r_j_m in r_j_m_list:
                    recording_jobs.append(r_j_m.recording_job)
            else:
                if u.has_key("event_id"):
                    r_j_m_list = RecordingJobMetadata.objects.filter(\
key="event_id",value=u["event_id"].strip()).iterator()
                    for r_j_m in r_j_m_list:
                        recording_jobs.append(r_j_m.recording_job)

            for k,v in u.iteritems():
                # Updating Recording
                try:
                    if recordings:
                        logger.info("Updating recordings")
                        for recording in recordings:
                            metadatas = json.loads(recording.metadata_json)
                            for m in metadatas:
                                for k1,v1 in m.iteritems():
                                    if k1 == k:
                                        logger.info(\
"Recording %s updated. %s = %s" % (recording,k1,v))
                                        m[k1] = v
                            recording.metadata_json = json.dumps(metadatas)
                            recording.save()
                            updating_problem = False
                except Exception, e:
                    logger.debug(\
"Unexpected updating Recording values: %s" % e)

                # Updating RecordingJobMetadata
                try:
                    if len(recording_jobs)>0:
                        logger.info("Updating recording_jobs")
                        for recording_job in recording_jobs:
                            r_j_m = RecordingJobMetadata.objects.filter(\
recording_job=recording_job,key=k).update(value=v.strip())
                            logger.info(\
"RecorderJob %s updated. %s = %s" % (recording_job,k,v))
                            updating_problem = False
                except Exception, e:
                    logger.debug(\
"Unexpected updating RecordingJobMetadata values: %s" % e)

            if updating_problem:
                res = {
                    "result": -1,
                    "response": "Parcial errors"
                }

    except Exception  as e:
        logger.error("Unexpected exception updating recordings info: %s" % (e))
        res = {
            "result": -1,
            "response": "Unexpected exception updating recordings info: %s" % (e)
        }

    return json_response(res)





