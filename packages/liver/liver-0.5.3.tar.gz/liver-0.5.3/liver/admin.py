from models import *

import logging
logger = logging.getLogger("liver.admin")

from django import forms
from django import template

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.contrib.admin import helpers
from django.contrib.admin.util import get_deleted_objects, model_ngettext
from django.db import router
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy, ugettext as _
from .forms import UploadFileForm

import utils

import datetime, time, pytz, calendar
import simplejson


def export_as_json(self, request, queryset):
    from django.http import HttpResponse
    response = HttpResponse(mimetype="text/javascript")
    response['Content-Disposition'] = 'attachment; filename=%s-%s-export-%s.json' % (
        __package__.lower(),
        queryset.model.__name__.lower(),
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
    )
    res_dict = []
    rs = RecordingSource.objects.all()
    for r in rs:
      res_dict.append(r.to_dict())
    res = simplejson.dump(res_dict, response, indent=4 )
    return response

def export_as_csv(self, request, queryset):
    from django.http import HttpResponse
    import csv

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s-%s-export-%s.csv' % (
        __package__.lower(),
        queryset.model.__name__.lower(),
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
    )

    writer = csv.writer(response)
    first_iter = True
    for o in queryset:
        if first_iter:
            headers = utils.get_model_field_names(o.__class__())
            writer.writerow(headers)
            first_iter = False
        values = utils.get_model_fields_values(o)
        writer.writerow(values)
    return response


def clone(modeladmin, request, queryset):
    for o in queryset:
        o.clone()
clone.short_description = _("Clone")

def import_from_json(modeladmin, request, queryset):
    print request
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    using = router.db_for_write(modeladmin.model)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post'):
        print request.POST
    
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # for chunk in request.FILES['file'].chunks():
            #     print chunk
            json = simplejson.load(request.FILES['file'])
            utils.from_dict_to_recording_source(json)
            return None
            modeladmin.message_user(request, _("Successfully imported.")
            , messages.SUCCESS)
        # Return None to display the change list page again.
        return None

    title = _("Import")
    form = UploadFileForm()

    context = {
        "title": title,
        "form": form,
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
    }

    # Display the confirmation page

    return TemplateResponse(request, ["admin/%s/import_action.html" % app_label]
    , context, current_app=modeladmin.admin_site.name)


class RecordingRuleInLine(admin.TabularInline):
        model = RecordingRule
        extra = 1

class RecordingMetadataInLine(admin.TabularInline):
        model = RecordingMetadata
        extra = 1

class RecordingJobMetadataInLine(admin.TabularInline):
        model = RecordingJobMetadata
        extra = 1

class RecordingSourceAdmin(admin.ModelAdmin):
    actions = [
            export_as_json,
            # export_as_csv,
            import_from_json,
            clone,
    ]

    inlines = [
                RecordingRuleInLine,
                RecordingMetadataInLine,
    ]

    list_display = [
            'sources_group',
            # 'insertion_date',
            'modification_date',
            'enabled',
            'enabled_since',
            'enabled_until',
            'edit_html',
    ]

    list_editable = [
            'sources_group',
            'enabled',
            'enabled_since',
            'enabled_until',

    ]

    list_display_links = ['edit_html']

    list_per_page = 200

    def edit_html(self, queryset):
        return '''<a href="%s/">Edit</a>''' % queryset.id
    edit_html.short_description = ''
    edit_html.allow_tags = True



class RecordingJobAdmin(admin.ModelAdmin):
    ordering = ['-scheduled_start_date']

    actions = [
            "wait",
            "cancel",
            "success",
            "launch_now",
            clone,
    ]

    def launch_now(self, request, queryset):
        d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
        for q in queryset:
            q.status="waiting"
            q.scheduled_start_date=d
            q.save()
    launch_now.short_description=_("Launch now")

    def wait(self, request, queryset):
        queryset.update(status="waiting")
    wait.short_description=_("Set to waiting")

    def cancel(self, request, queryset):
        queryset.update(status="cancelled")
    cancel.short_description=_("Set to cancelled")

    def success(self, request, queryset):
        queryset.update(status="successful")
    success.short_description=_("Set to successful")

    date_hierarchy = 'scheduled_start_date'

    list_per_page = 200

    search_fields = ['status','recordingjobmetadata__value' ]

    exclude = ["recording_source"]
    readonly_fields = [
            'insertion_date',
            'modification_date',
            'execution_date',
            'completion_date',
            'scheduled_end_date',
            'result',
    ]

    fieldsets = (
        (None, {
            'fields': (
                (
            'sources_group',
            'scheduled_start_date',
            'scheduled_end_date',
            'scheduled_duration',
            'enabled',
                ),

            )
        }),
        (_("Process"), {
            'fields': (
                (
            'status',
            'recorder',
                ),
                (
            'insertion_date',
            'modification_date',
            'execution_date',
            'completion_date',
                ),

            )
        }),

        (_("Log"), {
            'classes': ('collapse',),
            'fields': (
                ("result",
                ),
            )
        }),

    )

    list_display = [
      'pretty_name',
      'scheduled_start_date',
      'scheduled_end_date',
      'scheduled_duration',
      'insertion_date',
      'modification_date',
      'execution_date',
      'status',
    ]

    list_filter = [
            "enabled",
            "status",
            "recording_source",
            "recorder",
    ]

    inlines = [
        RecordingJobMetadataInLine,
    ]

class RecordingAdmin(admin.ModelAdmin):
    search_fields = ['name', 'metadata_json', 'profiles_json']

    ordering = ['-insertion_date']

    actions = [
            # clone,
    ]

    readonly_fields = [
            'name',
            'insertion_date',
            'modification_date',
            'recording_job',
            'profiles',
            'metadata',
    ]

    fieldsets = (
        (None, {
            'fields': (
                (
            'name',
            'insertion_date',
            'modification_date',
                ),

            )
        }),
        (_("Information"), {
            'fields': (
                (
            'profiles',
            'metadata',
                ),
            )
        }),

    )


    list_display = [
            'name',
            'insertion_date',
            'modification_date',
            'profiles',
            'metadata',
    ]

    list_per_page = 200

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        qs = super(RecordingAdmin, self).queryset(request)
        return qs.filter(Q(to_delete=False))


class SourceInLine(admin.TabularInline):
    model = Source
    fk_name = 'sources_group'
    extra = 0

class SourcesGroupAdmin(admin.ModelAdmin):
    actions = [
            clone,
    ]
    ordering = ['name']

    readonly_fields = [
            'insertion_date',
            'modification_date',
    ]

    fieldsets = (
        (None, {
            'fields': (
                (
            'name',
            'external_id',
                ),

            )
        }),
        (None, {
            'fields': (
                (
            'insertion_date',
            'modification_date',
                ),

            )
        }),
        (None, {
            'fields': (
                (
            'default_offset_start',
            'default_offset_end',
            'default_availability_window',
                ),

            )
        }),
    )

    inlines = [
      SourceInLine,
    ]


class RecorderAdmin(admin.ModelAdmin):
    ordering = ['name','token']


class ApplicationAdmin(admin.ModelAdmin):

    readonly_fields = [
            'id',
            'sync_time',
    ]

    list_editable = ['name','token', 'valid', 'valid_since','valid_until']

    list_display_links = ['edit_html']
    list_display = ('name', 'token', 'description',
            'valid', 'valid_since', 'valid_until',
            'modification_time', "edit_html")
    # list_filter = ['valid', 'source_host','enabled',
    #         ]
    search_fields = ['name', 'description','token',
            ]
    date_hierarchy = 'insertion_time'
    list_per_page = 200

    fieldsets = [
            (None,{
              'fields': [
                ('name','token'),
                ('valid','valid_since', 'valid_until','sync_time'),
                (),
            ]}),
            ('Other info', {
              'classes': ('collapse',),
              'fields': (
                ("description"),
              )
            }),
    ]

    def edit_html(self, queryset):
        return '''<a href="%s/">Edit</a>''' % queryset.id
    edit_html.short_description = ''
    edit_html.allow_tags = True



# admin.site.register(Source)
admin.site.register(SourcesGroup,SourcesGroupAdmin)
admin.site.register(Recorder,RecorderAdmin)
admin.site.register(RecordingSource,RecordingSourceAdmin)
admin.site.register(RecordingJob,RecordingJobAdmin)
admin.site.register(Recording,RecordingAdmin)
admin.site.register(Application,ApplicationAdmin)

