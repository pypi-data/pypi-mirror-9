from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy, ugettext as _

import datetime, time, pytz, calendar
import simplejson as json
import uuid

import utils

class SourcesGroup(models.Model):
    name = models.CharField(max_length=5000,verbose_name="Common Name")
    external_id = models.CharField(max_length=5000,verbose_name="External Id.")

    insertion_date = models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(auto_now=True,
            auto_now_add=True, blank=True, null=True)
    default_offset_start = models.IntegerField(null=True, blank=True,
            verbose_name="Default offset start (in seconds)")
    default_offset_end = models.IntegerField(null=True, blank=True,
            verbose_name="Default offset end (in seconds)")
    default_availability_window = models.IntegerField(null=True, blank=True,
            verbose_name="Default licensing window (in hours)")

    def clone(self):
        sg = SourcesGroup()
        if self.name and self.name.find(" (Clone") >= 0:
            sg.name = self.name[:self.name.find(" (Clone")] \
                    + " (Clone %s)" % int(time.time())
        else:
            sg.name = self.name + " (Clone %s)" % int(time.time())
        sg.external_id = self.external_id
        sg.default_offset_start = self.default_offset_start
        sg.default_offset_end = self.default_offset_end
        sg.default_availability_window = self.default_availability_window

        sg.save()

        for s in self.source_set.all():
            s_clone = s.clone()
            s_clone.sources_group = sg
            s_clone.save()

        return sg

    def to_dict(self,references=False):
        res = {}
        res["name"]=self.name
        res["external_id"]=self.external_id
        res["default_offset_start"]=self.default_offset_start
        res["default_offset_end"]=self.default_offset_end
        res["default_availability_window"]=self.default_availability_window
        res["insertion_time"]=utils.from_date_to_timestamp(self.insertion_date)
        res["modification_time"]=utils.from_date_to_timestamp(self.modification_date)
        res["sources"]=[]
        for s in self.source_set.all():
            res["sources"].append(s.to_dict(references=False))
        return res

    def load_dict(self, d):
        self.name = d["name"]
        self.external_id = d["external_id"]
        self.default_offset_start = d["default_offset_start"]
        self.default_offset_end = d["default_offset_end"]
        self.default_availability_window = d["default_availability_window"]
        self.save()
        self.source_set.all().delete()
        if d.has_key("sources") and d["sources"]:
            for dd in d["sources"]:
                s = Source()
                s.sources_group = self
                s.load_dict(dd)

        self.save()

    def save(self, *args, **kwargs):
        if not self.insertion_date:
            d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            self.insertion_date = d
        super(SourcesGroup, self).save(*args, **kwargs)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"%s [%s]" % (slugify(self.name),
                self.external_id)



class Source(models.Model):
    name = models.CharField(max_length=5000,verbose_name="Common Name")
    uri = models.CharField(max_length=5000,verbose_name="URI")
    bitrate = models.IntegerField(verbose_name="Bitrate (bps)",
            default=1000000)

    insertion_date = models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(auto_now=True,
            auto_now_add=True, blank=True, null=True)

    sources_group = models.ForeignKey(SourcesGroup, null=True, blank=True)

    def clone(self):
        s = Source()
        if self.name and self.name.find(" (Clone") >= 0:
            s.name = self.name[:self.name.find(" (Clone")] \
                    + " (Clone %s)" % int(time.time())
        else:
            s.name = self.name + " (Clone %s)" % int(time.time())
        s.bitrate = self.bitrate
        s.uri = self.uri
        s.save()
        return s

    def save(self, *args, **kwargs):
        if not self.insertion_date:
            d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            self.insertion_date = d
        super(Source, self).save(*args, **kwargs)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"%s [%s] [%s]" % (slugify(self.name), self.uri,self.bitrate)

    def to_dict(self,references=False):
        res = {}
        res["name"]=self.name
        res["uri"]=self.uri
        res["bitrate"]=self.bitrate
        res["insertion_time"]=utils.from_date_to_timestamp(self.insertion_date)
        res["modification_time"]=utils.from_date_to_timestamp(self.modification_date)
        if references:
            res["sources_group"]=self.sources_group.id
        return res

    def load_dict(self, d):
        self.name = d["name"]
        self.uri = d["uri"]
        self.bitrate = d["bitrate"]
        self.save()

class Recorder(models.Model):
    name = models.CharField(max_length=5000)
    token = models.CharField(max_length=5000,default=str(uuid.uuid1()))

    def clone(self):
        r = Recorder()
        if self.name and self.name.find(" (Clone") >= 0:
            r.name = self.name[:self.name.find(" (Clone")] \
                    + " (Clone %s)" % int(time.time())
        else:
            r.name = self.name + " (Clone %s)" % int(time.time())
        r.token = self.token
        r.save()
        return r

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s [%s]" % (self.name, self.token)

class RecordingSource(models.Model):
    external_id = models.CharField(max_length=5000,verbose_name="External Id.",
            default = "")
    sources_group = models.ForeignKey(SourcesGroup, null=True, blank=True, on_delete=models.SET_NULL)

    insertion_date = models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(auto_now=True,
            auto_now_add=True, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    enabled_since = models.DateTimeField(null=True, blank=True)
    enabled_until = models.DateTimeField(null=True, blank=True,
            default = None, verbose_name="Enabled to")

    def clone(self):
        rs = RecordingSource()
        rs.external_id = self.external_id
        rs.sources_group = self.sources_group
        rs.enabled = False
        rs.enabled_since = self.enabled_since
        rs.enabled_until = self.enabled_until
        rs.save()
        rm_list = RecordingMetadata.objects.filter(recording_source=self)
        for rm in rm_list:
            rm_clone = rm.clone()
            rm_clone.recording_source=rs
            rm_clone.save()
        rr_list = RecordingRule.objects.filter(recording_source=self)
        for rr in rr_list:
            rr_clone = rr.clone()
            rr_clone.recording_source=rs
            rr_clone.save()
        return rs

    def to_dict(self,references=False):
        res = {}
        res["enabled"]=self.enabled
        res["external_id"]=self.external_id

        if self.sources_group:
            res["sources_group"]=self.sources_group.to_dict(references=False)

        res["recording_metadata"]=[]
        rm_list = RecordingMetadata.objects.filter(recording_source=self)
        for rm in rm_list:
            res["recording_metadata"].append(rm.to_dict(references=False))

        res["recording_rules"]=[]
        rr_list = RecordingRule.objects.filter(recording_source=self)
        for rr in rr_list:
            res["recording_rules"].append(rr.to_dict(references=False))

        return res

    def load_dict(self, d):
        # replace new values from d dict in the RecordingSource object deleting
        # the older values
        self.external_id = d["external_id"]
        self.enabled = d["enabled"]

        self.save()

        if d.has_key("sources_group") and d["sources_group"]:
            try:
              sg = SourcesGroup.objects.filter(name=d["sources_group"]["name"])[0]
            except Exception, e:
              sg = SourcesGroup()
            sg.load_dict(d["sources_group"])
            self.sources_group = sg
        elif self.sources_group:
            self.sources_group = None

        RecordingMetadata.objects.filter(recording_source=self).delete()
        if d.has_key("recording_metadata") and d["recording_metadata"]:
            for dd in d["recording_metadata"]:
                rm = RecordingMetadata()
                rm.recording_source=self
                rm.load_dict(dd)

        RecordingRule.objects.filter(recording_source=self).delete()
        if d.has_key("recording_rules") and d["recording_rules"]:
            for dd in d["recording_rules"]:
                rr = RecordingRule()
                rr.recording_source=self
                rr.load_dict(dd)

        self.save()

    def save(self, *args, **kwargs):
        if not self.insertion_date:
            d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            self.insertion_date = d
        super(RecordingSource, self).save(*args, **kwargs)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "Recording %s" % (unicode(self.sources_group))


class RecordingMetadata(models.Model):
    recording_source = models.ForeignKey(RecordingSource)

    key = models.CharField(max_length=5000,blank=True)
    value = models.CharField(max_length=5000,blank=True)

    def clone(self):
        rm = RecordingMetadata()
        rm.recording_source = self.recording_source
        rm.key = self.key
        rm.value = self.value
        rm.save()
        return rm

    def to_dict(self,references=False):
        res = {}
        res["key"]=self.key
        res["value"]=self.value
        if references:
            res["recording_source"]=self.recording_source.id
        return res

    def load_dict(self, d):
        self.key = d["key"]
        self.value = d["value"]
        self.save()

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s - %s" % (self.key, self.value)


class RecordingRule(models.Model):
    recording_source = models.ForeignKey(RecordingSource)

    metadata_key_filter = models.CharField(max_length=5000,blank=True)
    metadata_value_filter = models.CharField(max_length=5000,blank=True)

    offset_start = models.IntegerField(null=True, blank=True,
            verbose_name="Offset start (in seconds)")
    offset_end = models.IntegerField(null=True, blank=True,
            verbose_name="Offset end(in seconds)")
    availability_window = models.IntegerField(null=True, blank=True,
            verbose_name="Licensing window (in hours)")

    def clone(self):
        rr = RecordingRule()
        rr.recording_source = self.recording_source
        rr.metadata_key_filter = self.metadata_key_filter
        rr.metadata_value_filter = self.metadata_value_filter
        rr.offset_start = self.offset_start
        rr.offset_end = self.offset_end
        rr.availability_window = self.availability_window
        rr.save()
        return rr

    def to_dict(self,references=False):
        res = {}
        res["metadata_key_filter"]=self.metadata_key_filter
        res["metadata_value_filter"]=self.metadata_value_filter
        res["offset_start"]=self.offset_start
        res["offset_end"]=self.offset_end
        res["availability_window"]=self.availability_window
        if references:
            res["recording_source"]=self.recording_source.id
        return res

    def load_dict(self, d):
        self.metadata_key_filter = d["metadata_key_filter"]
        self.metadata_value_filter = d["metadata_value_filter"]
        self.offset_start = d["offset_start"]
        self.offset_end = d["offset_end"]
        self.availability_window = d["availability_window"]
        self.save()

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "[%s:%s] [start:%s,end:%s] (%s)" \
    % (self.metadata_key_filter,
       self.metadata_value_filter,
       self.offset_start,
       self.offset_end,
       self.availability_window)


class RecordingJob(models.Model):
    class Meta:
        verbose_name = _('Recording job')

    status_choices = [
        ('waiting', _('Waiting')),
        ('running', _('Running')),
        ('failed', _('Failed')),
        ('successful', _('Successful')),
        ('cancelled', _('Cancelled')),
    ]

    recording_source = models.ForeignKey(RecordingSource, null=True, blank=True,
                        on_delete=models.SET_NULL)

    sources_group = models.ForeignKey(SourcesGroup)

    insertion_date = models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(auto_now=True,
            auto_now_add=True, blank=True, null=True)
    execution_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)

    scheduled_start_date = models.DateTimeField(null=True, blank=True)
    scheduled_end_date = models.DateTimeField(null=True, blank=True,
            editable=False)
    scheduled_duration = models.IntegerField(
            verbose_name="Duration (sec.)")

    enabled = models.BooleanField(default=True)

    recorder =  models.ForeignKey(Recorder, null=True, blank=True,
            on_delete=models.SET_NULL)

    result = models.TextField(max_length=50000, blank=True, null=True,
            verbose_name=_('Result'),default="None")
    status = models.CharField(max_length=5000,
            verbose_name=_('Status'),
            choices=status_choices)

    def get_scheduled_start_timestamp(self):
        return calendar.timegm(
            self.scheduled_start_date.astimezone(
                pytz.utc).utctimetuple())
    scheduled_start_timestamp = property(get_scheduled_start_timestamp)

    def clone(self):
        rj = RecordingJob()
        rj.recording_source = self.recording_source
        rj.sources_group = self.sources_group
        rj.scheduled_start_date = self.scheduled_start_date
        rj.scheduled_duration = self.scheduled_duration
        rj.enabled = self.enabled
        rj.save()
        rjm_list = RecordingJobMetadata.objects.filter(recording_job=self)
        for rjm in rjm_list:
            rjm_clone = rjm.clone()
            rjm_clone.recording_job=rj
            rjm_clone.save()
        return rj

    def save(self, *args, **kwargs):
        if not self.insertion_date:
            d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            self.insertion_date = d

        try:
            _timestamp = \
calendar.timegm(self.scheduled_start_date.astimezone(pytz.utc).utctimetuple())\
+self.scheduled_duration
            self.scheduled_end_date = datetime.datetime.fromtimestamp(_timestamp,pytz.UTC)
        except Exception, e:
            pass

        super(RecordingJob, self).save(*args, **kwargs)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "[%s] %s [start:%s, duration:%s]" \
    % (self.id,
       self.sources_group,
       self.scheduled_start_date,
       self.scheduled_duration)

    def slug(self):
        return slugify("%s-%s-%s-%s" \
    % (self.sources_group,
       self.scheduled_start_date,
       self.scheduled_duration,
       self.id))

    def pretty_name(self):
        try:
            title = self.recordingjobmetadata_set.filter(key="title")[0]
        except Exception:
            title = "-"
        return "[%s] %s [%s]" \
    % (self.id,
       self.sources_group,
       title)



class RecordingJobMetadata(models.Model):
    recording_job = models.ForeignKey(RecordingJob)

    key = models.CharField(max_length=5000,blank=True)
    value = models.CharField(max_length=5000,blank=True)

    def clone(self):
        rjm = RecordingJobMetadata()
        rjm.recording_job = self.recording_job
        rjm.key = self.key
        rjm.value = self.value
        rjm.save()
        return rjm

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s - %s" % (self.key, self.value)


class Recording(models.Model):
    recording_job = models.ForeignKey(RecordingJob, on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name="Associated recording job")
    recorder = models.ForeignKey(Recorder, on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name="Associated recorder")

    name = models.CharField(max_length=5000,blank=True,editable=False)

    insertion_date = models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(auto_now=True,
            auto_now_add=True, blank=True, null=True)

    metadata_json = models.TextField(max_length=5000,blank=True,editable=False) # json
    def get_metadata(self):
        try:
          res = ""
          m_list = json.loads(self.metadata_json)
          for m in m_list:
              res +=\
"%s:%s\n" % (m.keys()[0], m.values()[0])
        except Exception:
          res = self.metadata_json
        return res
    metadata = property(get_metadata)

    profiles_json = models.TextField(max_length=5000,blank=True,editable=False) # json
    def get_profiles(self):
        try:
          res = ""
          p_list = json.loads(self.profiles_json)
          for p in p_list:
              res +=\
"uri:%(uri)s file:%(destination)s\n"  % p

        except Exception:
          res = self.profiles_json
        return res
    profiles = property(get_profiles)

    to_delete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.insertion_date:
            d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
            self.insertion_date = d
        # TODO: Implementar la logica que decide si el flag to_delete se
        # activa o no
        super(Recording, self).save(*args, **kwargs)

    def delete(self, using=None):
        if self.to_delete:
            return super(Recording, self).delete()
        else:
            self.to_delete = True
            self.save()

    def clone(self):
        r = Recording()
        if self.name and self.name.find(" (Clone") >= 0:
            r.name = self.name[:self.name.find(" (Clone")] \
                    + " (Clone %s)" % int(time.time())
        else:
            r.name = self.name + " (Clone %s)" % int(time.time())

        r.metadata_json = self.metadata_json
        r.profiles_json = self.profiles_json
        r.recording_job = self.recording_job
        r.save()
        return r

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s" % (self.name)


class Application(models.Model):

    class Meta:
        verbose_name = 'External application'

    name = models.CharField(max_length=250, blank=True)
    description = models.TextField(max_length=2500, blank=True)

    token = models.CharField(max_length=500, blank=True)

    insertion_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, db_index=True)
    modification_time = models.DateTimeField(auto_now=True,
            auto_now_add=True, blank=True, db_index=True, null=True)
    valid = models.BooleanField(default=False)
    valid_since = models.DateTimeField(null=True, blank=True, db_index=True)
    valid_until = models.DateTimeField(null=True, blank=True, db_index=True,
            default = None)
    sync_time = models.DateTimeField(blank=True, db_index=True, null=True )


    def __unicode__(self):
        return "%s - %s" % (self.name,self.token)
    def save(self, *args, **kwargs):
        d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
        self.modification_time = d
        if not self.insertion_time:
            self.insertion_time = d
        if not self.token or len(self.token) == 0:
            self.token = str(uuid.uuid1())
        self.token = self.token.strip()

        super(Application, self).save(*args, **kwargs)



