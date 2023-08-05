"""Miscellaneous utilities."""

from pydoctor import model

from twisted.web.template import tags

import os, urllib

def link(o):
    if not o.isVisible:
        o.system.warning("html", "don't link to %s"%o.fullName())
    return o.system.urlprefix+urllib.quote(o.fullName()+'.html')

def srclink(o):
    return o.sourceHref

def templatefile(filename):
    abspath = os.path.abspath(__file__)
    pydoctordir = os.path.dirname(os.path.dirname(abspath))
    return os.path.join(pydoctordir, 'templates', filename)

def fillSlots(tag, **kw):
    for k, v in kw.iteritems():
        tag = tag.fillSlots(k, v)
    return tag

def taglink(o, label=None):
    if not o.isVisible:
        o.system.warning("html", "don't link to %s"%o.fullName())
    if label is None:
        label = o.fullName()
    if o.documentation_location == model.DocLocation.PARENT_PAGE:
        p = o.parent
        if isinstance(p, model.Module) and p.name == '__init__':
            p = p.parent
        linktext = link(p) + '#' + urllib.quote(o.name)
    elif o.documentation_location == model.DocLocation.OWN_PAGE:
        linktext = link(o)
    else:
        raise AssertionError(
            "Unknown documentation_location: %s" % o.documentation_location)
    return tags.a(href=linktext)(label)
