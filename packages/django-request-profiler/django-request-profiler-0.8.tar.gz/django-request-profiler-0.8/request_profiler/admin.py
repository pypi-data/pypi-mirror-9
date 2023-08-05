# -*- coding: utf-8 -*-
# admin models for request_profiler app
from django.contrib import admin

from request_profiler import models


class RuleSetAdmin(admin.ModelAdmin):

    list_display = (
        'enabled',
        'uri_regex',
        'user_filter_type',
        'user_group_filter',
    )

admin.site.register(
    models.RuleSet,
    RuleSetAdmin
)


class ProfilingRecordAdmin(admin.ModelAdmin):

    list_display = (
        'start_ts',
        'user',
        'session_key',
        'remote_addr',
        'http_method',
        'request_uri',
        'view_func_name',
        'response_status_code',
        'duration',
    )

admin.site.register(
    models.ProfilingRecord,
    ProfilingRecordAdmin
)
