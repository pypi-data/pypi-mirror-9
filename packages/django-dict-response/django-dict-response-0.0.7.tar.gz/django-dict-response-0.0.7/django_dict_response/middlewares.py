# coding: utf-8
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
import string

render_keys = ['context_instance', 'current_app', 'dirs', 'status',
               'template_name']
json_keys = ['reason', 'encoder', 'safe', 'status']
all_keys = render_keys + json_keys


class DictResponseMiddleware(object):
    def is_header(self, key):
        return key[0] in string.ascii_uppercase

    def template_name(self, request):
        if request.resolver_match.namespaces:
            namespaces = '/'.join(request.resolver_match.namespaces)
            return namespaces + '/' + request.resolver_match.url_name + '.html'
        return request.resolver_match.func.__name__ + '.html'

    def process_response(self, request, response):
        if not isinstance(response, dict):
            return response
        redirect_key = getattr(settings, 'REDIRECT_KEY', 'redirect_to')
        if redirect_key in response:
            redirect_to = response[redirect_key]
            if not isinstance(redirect_to, (list, tuple)):
                redirect_to = [redirect_to]
            return redirect(*redirect_to)
        is_json = response.get('content_type', '') == 'application/json'
        keys = json_keys if is_json else render_keys
        headers = {k: v for k, v in response.items() if self.is_header(k)}
        kwargs = {k: v for k, v in response.items() if k in keys}
        dictionary = {k: v for k, v in response.items()
                      if k not in headers and k not in all_keys}
        if is_json:
            new_response = JsonResponse(dictionary, **kwargs)
        else:
            if 'template_name' not in kwargs:
                kwargs['template_name'] = self.template_name(request)
            new_response = render(request, dictionary=dictionary, **kwargs)
        for k, v in headers.items():
            new_response[k] = v
        return new_response
