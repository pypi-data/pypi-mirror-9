# -*- coding:utf-8 -*-

# Author: Pablo Saavedra Rodinho
# Contact: pablo.saavedra@interoud.com

import time
import calendar
import dateutil.parser
import pytz

import  models

def from_dict_to_recording_source(o, in_list=False):


    # We accept also list of dicts, if list assumes a list of dicts
    if isinstance(o, list):
        for v in o:
            from_dict_to_recording_source(v)
    else: # Assumes a dict with a RecordingSource representation
        o["external_id"]
        rs_found=False
        for rs in models.RecordingSource.objects\
                .filter(external_id=o["external_id"]).iterator():
            rs_found=True
            rs.load_dict(o)
        if not rs_found:
            rs = models.RecordingSource()
            rs.load_dict(o)

def from_date_string_to_timestamp(date_txt):
    return int(calendar.timegm(dateutil.parser.parse(date_txt).utctimetuple()))

def from_date_to_timestamp(date):
    return int(calendar.timegm(date.astimezone(pytz.utc).utctimetuple()))

def get_model_fields(model):
    return model._meta.fields

def get_model_field_names(model):
    res = []
    for field in get_model_fields(model):
        f = field.name
        res.append(f)
    return res

def get_model_fields_values(modelobj):
    res = []
    for field in get_model_fields(modelobj):
        f = str(getattr(modelobj, field.name))
        res.append(f)
    return res


