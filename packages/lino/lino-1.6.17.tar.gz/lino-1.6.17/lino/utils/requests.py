# Copyright 2009 Luc Saffre
# License: BSD (see file COPYING for details)


import os


def again(request, *args, **kw):
    get = request.GET.copy()
    for k, v in kw.items():
        if v is None:  # value None means "remove this key"
            if get.has_key(k):
                del get[k]
        else:
            get[k] = v
    path = request.path
    if len(args):
        path += "/" + "/".join(args)
    path = os.path.normpath(path)
    path = path.replace("\\", "/")
    s = get.urlencode()
    if len(s):
        path += "?" + s
    # print pth
    return path


def get_redirect(request):
    if hasattr(request, "redirect_to"):
        return request.redirect_to


def redirect_to(request, url):
    request.redirect_to = url



#~ def is_editing(request):
    #~ editing = request.GET.get("editing",None)
    #~ if editing is None:
        #~ path = request.session.get("editing",None)
    #~ else:
        #~ editing = int(editing)
        #~ if editing:
            #~ request.session["editing"] = path = request.path
        #~ else:
            #~ request.session["editing"] = path = None
    #~ if request.path == path:
        #~ return True
    #~ request.session["editing"] = None
    #~ return False

#~ def stop_editing(request):
    #~ request.session["editing"] = None

#~ def start_editing(request):
    #~ request.session["editing"] = request.path
