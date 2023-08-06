# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.import logging

import json
import logging
import urllib

from django.conf import settings  # noqa
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse  # noqa
from django.views.generic import TemplateView  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from monitoring.overview import constants
from monitoring.alarms import tables as alarm_tables
from monitoring import api

LOG = logging.getLogger(__name__)
OVERVIEW = [
    {'name': _('OpenStack Services'),
     'groupBy': 'service'},
    {'name': _('Servers'),
     'groupBy': 'hostname'}
]

DEFAULT_LINKS = [
    {'title': 'Dashboard', 'fileName': 'openstack.json'},
    {'title': 'Monasca Health', 'fileName': 'monasca.json'}
]

SERVICES = getattr(settings, 'MONITORING_SERVICES', OVERVIEW)
DASHBOARDS = getattr(settings, 'GRAFANA_LINKS', DEFAULT_LINKS)


def get_icon(status):
    if status == 'chicklet-success':
        return constants.OK_ICON
    if status == 'chicklet-error':
        return constants.CRITICAL_ICON
    if status == 'chicklet-warning':
        return constants.WARNING_ICON
    if status == 'chicklet-unknown':
        return constants.UNKNOWN_ICON
    if status == 'chicklet-notfound':
        return constants.NOTFOUND_ICON


priorities = [
    {'status': 'chicklet-success', 'severity': 'OK'},
    {'status': 'chicklet-unknown', 'severity': 'UNDETERMINED'},
    {'status': 'chicklet-warning', 'severity': 'LOW'},
    {'status': 'chicklet-warning', 'severity': 'MEDIUM'},
    {'status': 'chicklet-warning', 'severity': 'HIGH'},
    {'status': 'chicklet-error', 'severity': 'CRITICAL'},
]
index_by_severity = {d['severity']: i for i, d in enumerate(priorities)}


def show_by_dimension(data, dim_name):
    if 'dimensions' in data['metrics'][0]:
        dimensions = data['metrics'][0]['dimensions']
        if dim_name in dimensions:
            return str(data['metrics'][0]['dimensions'][dim_name])
    return ""


def get_status(alarms):
    if not alarms:
        return 'chicklet-notfound'
    status_index = 0
    for a in alarms:
        severity = alarm_tables.show_severity(a)
        severity_index = index_by_severity[severity]
        status_index = max(status_index, severity_index)
    return priorities[status_index]['status']


def generate_status(request):
    try:
        alarms = api.monitor.alarm_list(request)
    except Exception:
        alarms = []
    alarms_by_service = {}
    for a in alarms:
        service = alarm_tables.get_service(a)
        service_alarms = alarms_by_service.setdefault(service, [])
        service_alarms.append(a)
    for row in SERVICES:
        row['name'] = unicode(row['name'])
        if 'groupBy' in row:
            alarms_by_group = {}
            for a in alarms:
                group = show_by_dimension(a, row['groupBy'])
                if group:
                    group_alarms = alarms_by_group.setdefault(group, [])
                    group_alarms.append(a)
            services = []
            for group, group_alarms in alarms_by_group.items():
                service = {
                    'display': group,
                    'name': "%s=%s" % (row['groupBy'], group),
                    'class': get_status(group_alarms)
                }
                service['icon'] = get_icon(service['class'])
                services.append(service)
            row['services'] = services
        else:
            for service in row['services']:
                service_alarms = alarms_by_service.get(service['name'], [])
                service['class'] = get_status(service_alarms)
                service['icon'] = get_icon(service['class'])
                service['display'] = unicode(service['display'])
    return SERVICES


class IndexView(TemplateView):
    template_name = constants.TEMPLATE_PREFIX + 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        proxy_url_path = str(reverse_lazy(constants.URL_PREFIX + 'proxy'))
        api_root = self.request.build_absolute_uri(proxy_url_path)
        context["api"] = api_root
        context["dashboards"] = DASHBOARDS
        return context


class MonascaProxyView(TemplateView):
    template_name = ""

    def _convert_dimensions(self, req_kwargs):
        """this method converts the dimension string
        service:monitoring  (requested by a query string arg)
        into a python dict that looks like
        {"service": "monitoring"} (used by monasca api calls)
        """
        new_dimenstion_dict = {}
        if 'dimensions' in req_kwargs:
            dimensions_str = req_kwargs['dimensions'][0]
            print(dimensions_str)
            print(type(dimensions_str))
            dimensions_str_array = dimensions_str.split(',')
            for dimension in dimensions_str_array:
                dimension_name_value = dimension.split(':')
                if len(dimension_name_value) == 2:
                    new_dimenstion_dict[dimension_name_value[0]] = urllib.unquote(dimension_name_value[1]).decode('utf8')
                else:
                    raise Exception('Dimensions are malformed')

            req_kwargs['dimensions'] = new_dimenstion_dict
        return req_kwargs

    def get(self, request, *args, **kwargs):
        # monasca_endpoint = api.monitor.monasca_endpoint(self.request)
        restpath = self.kwargs['restpath']

        results = None
        parts = restpath.split('/')
        if "metrics" == parts[0]:
            req_kwargs = dict(self.request.GET)
            self._convert_dimensions(req_kwargs)
            if len(parts) == 1:
                results = {'elements': api.monitor.
                           metrics_list(request,
                                        **req_kwargs)}
            elif "statistics" == parts[1]:
                results = {'elements': api.monitor.
                           metrics_stat_list(request,
                                             **req_kwargs)}
            elif "measurements" == parts[1]:
                results = {'elements': api.monitor.
                           metrics_measurement_list(request,
                                                    **req_kwargs)}
        if not results:
            LOG.warn("There was a request made for the path %s that"
                     " is not supported." % restpath)
            results = {}
        return HttpResponse(json.dumps(results),
                            content_type='application/json')


class StatusView(TemplateView):
    template_name = ""

    def get(self, request, *args, **kwargs):
        ret = {
            'series': generate_status(self.request),
            'settings': {}
        }

        return HttpResponse(json.dumps(ret),
                            content_type='application/json')
