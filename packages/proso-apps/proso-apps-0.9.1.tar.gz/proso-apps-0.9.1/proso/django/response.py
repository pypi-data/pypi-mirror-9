# -*- coding: utf-8 -*-
from django.shortcuts import render as original_render, redirect
from django.http import HttpResponse
import json as simplejson
import markdown
import logging
from time import time
import proso.django.log


LOGGER = logging.getLogger('django.request')


def redirect_pass_get(request, view, *args, **kwargs):
    response = redirect(view, *args, **kwargs)
    response['location'] = pass_get_parameters(request, response['location'])
    return response


def pass_get_parameters_string(request, ignore=None):
    ignore = [] if ignore is None else ignore
    to_pass = filter(lambda (k, v): k not in ignore, request.GET.items())
    return '&'.join(map(lambda (key, value): '%s=%s' % (key, value), to_pass))


def append_get_parameters(dest_url, get_parameters_string):
    prefix = '&' if dest_url.find('?') != -1 else '?'
    return dest_url + prefix + get_parameters_string


def pass_get_parameters(request, dest_url, ignore=None):
    return append_get_parameters(dest_url, pass_get_parameters_string(request, ignore))


def render(request, template, data, *args, **kwargs):
    help_text = None
    if 'help_text' in kwargs:
        help_text = kwargs['help_text']
        del kwargs['help_text']
    if help_text is not None:
        help_text = markdown.markdown(help_text)
    if help_text is not None or 'help_text' not in data:
        data['help_text'] = help_text
    return original_render(request, template, data, *args, **kwargs)


def render_json(request, json, template=None, status=None, help_text=None):
    time_start = time()
    if status is None or status == 200:
        json = {'data': json}
    if 'debug' in request.GET and request.user.is_staff and proso.django.log.is_log_prepared():
        json['debug_log'] = proso.django.log.get_request_log()
    if 'html' in request.GET:
        if help_text is not None:
            help_text = markdown.markdown(help_text)
        result = render(request, template, {'json': json, 'help_text': help_text}, status=status)
    else:
        result = JsonResponse(json, status=status)
    LOGGER.debug("rendering JSON response in %s seconds", (time() - time_start))
    return result


class JsonResponse(HttpResponse):

    """
        JSON response
    """

    def __init__(self, content, mimetype='application/json',
                 status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=simplejson.dumps(content),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )
