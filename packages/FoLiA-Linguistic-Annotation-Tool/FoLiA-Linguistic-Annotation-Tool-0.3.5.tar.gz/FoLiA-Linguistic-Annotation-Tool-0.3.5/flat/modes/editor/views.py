from __future__ import print_function, unicode_literals, division, absolute_import
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseForbidden
import sys
if sys.version < '3':
    from urllib2 import URLError
else:
    from urllib.error import URLError
from django.conf import settings
import flat.comm
import flat.users
from flat.views import initdoc, fatalerror
import json



@login_required
def view(request, namespace, docid):
    """The initial view, does not provide the document content yet"""
    if flat.users.models.hasreadpermission(request.user.username, namespace):
        if 'autodeclare' in settings.CONFIGURATIONS[request.session['configuration']]:
            if flat.users.models.haswritepermission(request.user.username, namespace):
                for annotationtype, set in settings.CONFIGURATIONS[request.session['configuration']]['autodeclare']:
                    try:
                        r = flat.comm.query(request, "USE " + namespace + "/" + docid + " DECLARE " + annotationtype + " OF " + set)
                    except Exception as e:
                        return fatalerror(request,e)

        return initdoc(request, namespace,docid, 'editor', 'editor.html')
    else:
        return fatalerror("Permission denied")


@login_required
def history(request,namespace, docid):
    if flat.users.models.hasreadpermission(request.user.username, namespace):
        try:
            if hasattr(request, 'body'):
                d = flat.comm.get(request, '/getdochistory/' +namespace + '/' + docid + '/',False)
            else:
                d = flat.comm.get(request, '/getdochistory/' +namespace + '/' + docid + '/',False)
        except URLError as e:
            return HttpResponseForbidden("Unable to connect to the document server: " + e.reason + " [editor/history]")
        return HttpResponse(json.dumps(d).encode('utf-8'), content_type='application/json')
    else:
        return HttpResponseForbidden("Permission denied, no read access")

@login_required
def revert(request,namespace, docid, commithash):
    if flat.users.models.haswritepermission(request.user.username, namespace):
        try:
            if hasattr(request, 'body'):
                flat.comm.get(request, '/revert/' +namespace + '/' + docid + '/?commithash=' + commithash,False)
            else:
                flat.comm.get(request, '/revert/' +namespace + '/' + docid + '/?commithash=' + commithash,False)
        except URLError as e:
            return HttpResponseForbidden("Unable to connect to the document server: " + e.reason + " [editor/revert]")
        return HttpResponse("{}", content_type='application/json') #no content, client will do a full reload
    else:
        return HttpResponseForbidden("Permission denied, no write access")
