from __future__ import print_function, unicode_literals, division, absolute_import
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
import flat.comm
import flat.users
from flat.views import initdoc, query
import json
import sys
if sys.version < '3':
    from urllib2 import URLError
else:
    from urllib.error import URLError



@login_required
def view(request, namespace, docid):
    """The initial viewer, does not provide the document content yet"""
    return initdoc(request, namespace,docid, 'viewer', 'viewer.html')

@login_required
def poll(request, namespace, docid):
    if flat.users.models.hasreadpermission(request.user.username, namespace):
        try:
            r = flat.comm.get(request, '/poll/' + namespace + '/' + docid + '/', False)
        except URLError:
            return HttpResponseForbidden("Unable to connect to the document server [viewer/poll]")
        return HttpResponse(r, content_type='application/json')
    else:
        return HttpResponseForbidden("Permission denied")

