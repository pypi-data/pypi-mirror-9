from __future__ import print_function, unicode_literals, division, absolute_import
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseForbidden
import flat.settings as settings
import flat.comm
import flat.users
import flat.modes.viewer.views
import json


@login_required
def view(request, namespace, docid):
    if flat.users.models.hasreadpermission(request.user.username, namespace):
        try:
            doc = flat.comm.query(request, "USE " + namespace + "/" + docid + " SELECT ALL FORMAT flat", setdefinitions=True,declarations=True) #get the entire document with meta information
        except URLError:
            return HttpResponseForbidden("Unable to connect to the document server [viewer/view]")
        d = flat.modes.viewer.views.getcontext(request,namespace,docid, doc)
        d['mode'] = 'structureeditor'
        return render(request, 'structureeditor.html', d)
    else:
        return HttpResponseForbidden("Permission denied")


#@login_required
#def annotate(request,namespace, docid):
#    if flat.users.models.haswritepermission(request.user.username, namespace):
#        d = flat.comm.postjson(request, '/annotate/' +namespace + '/' + docid + '/', request.body)
#        return HttpResponse(json.dumps(d), mimetype='application/json')
#    else:
#        return HttpResponseForbidden("Permission denied, no write access")




