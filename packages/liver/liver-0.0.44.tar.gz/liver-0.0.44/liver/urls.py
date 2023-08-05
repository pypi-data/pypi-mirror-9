
from django.conf.urls import *


urlpatterns = patterns('liver.views',
        (r'^api/external/get_worker_jobs$',
        'api_external_get_worker_jobs',
        None, 'api-external-get-worker-jobs'),
        (r'^api/external/notify_worker_jobs_result$',
        'api_external_notify_worker_jobs_result',
        None, 'api-external-notify-worker-jobs-result'),
        ( r'^api/external/get_mo_to_delete$',
        'api_external_get_mo_to_delete',
        None, "api_external_get_mo_to_delete"),
        ( r'^api/external/get_mo$',
        'api_external_get_mo',
        None, "api_external_get_mo"),
        ( r'^api/external/update_recordings$',
        'api_external_update_recordings',
        None, "api_external_update_recordings"),


)
