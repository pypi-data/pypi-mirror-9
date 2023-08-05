"""Convert epydoc markup into renderable content."""

import __builtin__
import exceptions
import inspect
import itertools
import os
import re
import sys
import urllib

from twisted.web.template import Tag, tags, XMLString

from pydoctor import model


STDLIB_DIR = os.path.dirname(os.__file__)
STDLIB_URL = 'http://docs.python.org/library/'


def link(o):
    return o.system.urlprefix + urllib.quote(o.fullName()+'.html')


def get_parser(formatname):
    try:
        mod = __import__('epydoc.markup.' + formatname,
                         globals(), locals(), ['parse_docstring'])
    except ImportError, e:
        return None, e
    else:
        return mod.parse_docstring, None


def boringDocstring(doc, summary=False):
    """Generate an HTML representation of a docstring in a really boring way.
    """
    # inspect.getdoc requires an object with a __doc__ attribute, not
    # just a string :-(
    if doc is None or not doc.strip():
        return '<pre class="undocumented">Undocumented</pre>'
    def crappit(): pass
    crappit.__doc__ = doc
    return (tags.pre, tags.tt)[bool(summary)](inspect.getdoc(crappit))


def stdlib_doc_link_for_name(name):
    parts = name.split('.')
    for i in range(len(parts), 0, -1):
        sub_parts = parts[:i]
        filename = '/'.join(sub_parts)
        sub_name = '.'.join(sub_parts)
        if sub_name == 'os.path' \
               or os.path.exists(os.path.join(STDLIB_DIR, filename) + '.py') \
               or os.path.exists(os.path.join(STDLIB_DIR, filename, '__init__.py')) \
               or os.path.exists(os.path.join(STDLIB_DIR, 'lib-dynload', filename) + '.so') \
               or sub_name in sys.builtin_module_names:
            return STDLIB_URL + sub_name + '.html#' + name
    part0 = parts[0]
    if part0 in __builtin__.__dict__ and not part0.startswith('__'):
        bltin = __builtin__.__dict__[part0]
        if part0 in exceptions.__dict__:
            return STDLIB_URL + 'exceptions.html#exceptions.' + name
        elif isinstance(bltin, type):
            return STDLIB_URL + 'stdtypes.html#' + name
        elif callable(bltin):
            return STDLIB_URL + 'functions.html#' + name
        else:
            return STDLIB_URL + 'constants.html#' + name
    return None


class _EpydocLinker(object):

    def __init__(self, obj):
        self.obj = obj

    def translate_indexterm(self, something):
        # X{foobar} is meant to put foobar in an index page (like, a
        # proper end-of-the-book index). Should we support that? There
        # are like 2 uses in Twisted.
        return de_p(something.to_html(self))

    def _objLink(self, obj, prettyID):
        if obj.documentation_location == model.DocLocation.PARENT_PAGE:
            p = obj.parent
            if isinstance(p, model.Module) and p.name == '__init__':
                p = p.parent
            linktext = link(p) + '#' + urllib.quote(obj.name)
        elif obj.documentation_location == model.DocLocation.OWN_PAGE:
            linktext = link(obj)
        else:
            raise AssertionError(
                "Unknown documentation_location: %s" % obj.documentation_location)
        return '<a href="%s"><code>%s</code></a>'%(linktext, prettyID)

    def look_for_name(self, name, candidates):
        part0 = name.split('.')[0]
        potential_targets = []
        for src in candidates:
            if part0 not in src.contents:
                continue
            target = src.resolveName(name)
            if target is not None and target not in potential_targets:
                potential_targets.append(target)
        if len(potential_targets) == 1:
            return potential_targets[0]
        elif len(potential_targets) > 1:
            self.obj.system.msg(
                "translate_identifier_xref", "%s:%s ambiguous ref to %s, could be %s" % (
                    self.obj.fullName(), self.obj.linenumber, name,
            ', '.join([ob.fullName() for ob in potential_targets])),
                thresh=-1)
        return None

    def look_for_intersphinx(self, name):
        """
        Return link for `name` based on intersphinx inventory.

        Return None if link is not found.
        """
        return self.obj.system.intersphinx.getLink(name)

    def translate_identifier_xref(self, fullID, prettyID):
        """Figure out what ``L{fullID}`` should link to.

        There is a lot of DWIM here.  The order goes:

          1. Check if fullID refers to an object by Python name resolution in
             our context.

          2. Walk up the object tree and see if fullID refers to an object by
             Python name resolution in each context.

          3. Check if fullID is the fullName of an object.

          4. Check to see if fullID names a builtin or standard library
             module.

          4. Walk up the object tree again and see if fullID refers to an
             object in an "uncle" object.  (So if p.m1 has a class C, the
             docstring for p.m2 can say L{C} to refer to the class in m1).  If
             at any level fullID refers to more than one object, complain.

          5. Examine every module and package in the system and see if fullID
             names an object in each one.  Again, if more than one object is
             found, complain.

        """
        src = self.obj
        while src is not None:
            target = src.resolveName(fullID)
            if target is not None:
                return self._objLink(target, prettyID)
            src = src.parent
        target = self.obj.system.objForFullName(fullID)
        if target is not None:
            return self._objLink(target, prettyID)
        fullerID = self.obj.expandName(fullID)
        linktext = stdlib_doc_link_for_name(fullerID)
        if linktext is not None:
            return '<a href="%s"><code>%s</code></a>'%(linktext, prettyID)
        src = self.obj
        while src is not None:
            target = self.look_for_name(fullID, src.contents.values())
            if target is not None:
                return self._objLink(target, prettyID)
            src = src.parent
        target = self.look_for_name(fullID, itertools.chain(
            self.obj.system.objectsOfType(model.Module),
            self.obj.system.objectsOfType(model.Package)))
        if target is not None:
            return self._objLink(target, prettyID)

        target = self.look_for_intersphinx(fullID)
        if target:
            return '<a href="%s"><code>%s</code></a>'%(target, prettyID)

        self.obj.system.msg(
            "translate_identifier_xref", "%s:%s invalid ref to %s" % (
                self.obj.fullName(), self.obj.linenumber, fullID),
            thresh=-1)
        return '<code>%s</code>'%(prettyID,)


class FieldDesc(object):
    def __init__(self):
        self.kind = None
        self.name = None
        self.type = None
        self.body = None
    def format(self):
        if self.body is None:
            body = ''
        else:
            body = self.body
        if self.type is not None:
            body = body, ' (type: ', self.type, ')'
        return body
    def __repr__(self):
        contents = []
        for k, v in self.__dict__.iteritems():
            contents.append("%s=%r"%(k, v))
        return "<%s(%s)>"%(self.__class__.__name__, ', '.join(contents))


def format_desc_list(singular, descs, plural=None):
    if plural is None:
        plural = singular + 's'
    if not descs:
        return ''
    if len(descs) > 1:
        label = plural
    else:
        label = singular
    r = []
    first = True
    for d in descs:
        if first:
            row = tags.tr(class_="fieldStart")
            row(tags.td(class_="fieldName")(label))
            first = False
        else:
            row = tags.tr()
            row(tags.td())
        if d.name is None:
            row(tags.td(colspan="2")(d.format()))
        else:
            row(tags.td(class_="fieldArg")(d.name), tags.td(d.format()))
        r.append(row)
    return r

def format_field_list(obj, singular, fields, plural=None):
    if plural is None:
        plural = singular + 's'
    if not fields:
        return ''
    if len(fields) > 1:
        label = plural
    else:
        label = singular
    rows = []
    first = True
    for field in fields:
        if first:
            row = tags.tr(class_="fieldStart")
            row(tags.td(class_="fieldName")(label))
            first=False
        else:
            row = tags.tr()
            row(tags.td())
        row(tags.td(colspan="2")(field.body))
        rows.append(row)
    return rows


_ok_chars = '\r\n\t\f'
_class = ''
for _c in map(chr, range(0, 32)):
    if _c not in _ok_chars:
        _class += _c
_control_pat = re.compile('[' + _class + ']')


def html2stan(crap):
    crap = _control_pat.sub(lambda m:'\\x%02x'%ord(m.group()), crap)
    crap = "<div>" + crap + "</div>"
    crap = XMLString(crap).load()[0].children
    if crap and crap[-1] == u'\n':
        del crap[-1]
    return crap

class Field(object):
    """Like epydoc.markup.Field, but without the gross accessor
    methods and with a formatted body."""
    def __init__(self, field, obj):
        self.tag = field.tag()
        self.arg = field.arg()
        self.body = html2stan(field.body().to_html(_EpydocLinker(obj)))

    def __repr__(self):
        r = repr(self.body)
        if len(r) > 25:
            r = r[:20] + '...' + r[-2:]
        return "<%s %r %r %s>"%(self.__class__.__name__,
                             self.tag, self.arg, r)

class FieldHandler(object):
    def __init__(self, obj):
        self.obj = obj

        self.types = {}

        self.parameter_descs = []
        self.return_desc = None
        self.raise_descs = []
        self.seealsos = []
        self.notes = []
        self.authors = []
        self.sinces = []
        self.unknowns = []
        self.unattached_types = {}

    def redef(self, field):
        self.obj.system.msg(
            "epytext",
            "on %r: redefinition of @type %s"%(self.obj.fullName(), field.arg),
            thresh=-1)

    def handle_return(self, field):
        if not self.return_desc:
            self.return_desc = FieldDesc()
        if self.return_desc.body:
            self.obj.system.msg('epydoc2stan', 'XXX')
        self.return_desc.body = field.body
    handle_returns = handle_return

    def handle_returntype(self, field):
        if not self.return_desc:
            self.return_desc = FieldDesc()
        if self.return_desc.type:
            self.obj.system.msg('epydoc2stan', 'XXX')
        self.return_desc.type = field.body
    handle_rtype = handle_returntype

    def add_type_info(self, desc_list, field):
        #print desc_list, field
        if desc_list and desc_list[-1].name == field.arg:
            if desc_list[-1].type is not None:
                self.redef(field)
            desc_list[-1].type = field.body
        else:
            d = FieldDesc()
            d.kind = field.tag
            d.name = field.arg
            d.type = field.body
            desc_list.append(d)

    def add_info(self, desc_list, field):
        d = FieldDesc()
        d.kind = field.tag
        d.name = field.arg
        d.body = field.body
        desc_list.append(d)

    def handle_type(self, field):
        self.types[field.arg] = field.body

    def handle_param(self, field):
        self.add_info(self.parameter_descs, field)
    handle_arg = handle_param
    handle_keyword = handle_param


    def handled_elsewhere(self, field):
        # Some fields are handled by extract_fields below.
        pass

    handle_ivar = handled_elsewhere
    handle_cvar = handled_elsewhere
    handle_var = handled_elsewhere

    def handle_raises(self, field):
        self.add_info(self.raise_descs, field)
    handle_raise = handle_raises

    def handle_seealso(self, field):
        self.seealsos.append(field)
    handle_see = handle_seealso

    def handle_note(self, field):
        self.notes.append(field)

    def handle_author(self, field):
        self.authors.append(field)

    def handle_since(self, field):
        self.sinces.append(field)

    def handleUnknownField(self, field):
        self.obj.system.msg(
            'epydoc2stan',
            'found unknown field on %r: %r'%(self.obj.fullName(), field),
            thresh=-1)
        self.add_info(self.unknowns, field)

    def handle(self, field):
        m = getattr(self, 'handle_' + field.tag, self.handleUnknownField)
        m(field)

    def resolve_types(self):
        for pd in self.parameter_descs:
            if pd.name in self.types:
                pd.type = self.types[pd.name]

    def format(self):
        r = []

        r.append(format_desc_list('Parameters', self.parameter_descs, 'Parameters'))
        if self.return_desc:
            r.append(tags.tr(class_="fieldStart")(tags.td(class_="fieldName")('Returns'),
                               tags.td(colspan="2")(self.return_desc.format())))
        r.append(format_desc_list("Raises", self.raise_descs, "Raises"))
        for s, p, l in (('Author', 'Authors', self.authors),
                        ('See Also', 'See Also', self.seealsos),
                        ('Present Since', 'Present Since', self.sinces),
                        ('Note', 'Notes', self.notes)):
            r.append(format_field_list(self.obj, s, l, p))
        unknowns = {}
        unknownsinorder = []
        for fieldinfo in self.unknowns:
            tag = fieldinfo.kind
            if tag in unknowns:
                unknowns[tag].append(fieldinfo)
            else:
                unknowns[tag] = [fieldinfo]
                unknownsinorder.append(unknowns[tag])
        for fieldlist in unknownsinorder:
            label = "Unknown Field: " + fieldlist[0].kind
            r.append(format_desc_list(label, fieldlist, label))

        return tags.table(class_='fieldTable')(r)


def de_p(s):
    if s.startswith('<p>') and s.endswith('</p>\n'):
        s = s[3:-5] # argh reST
    if s.endswith('\n'):
        s = s[:-1]
    return s


def reportErrors(obj, errs):
    for err in errs:
        if isinstance(err, str):
            linenumber = '??'
            descr = err
        else:
            linenumber = obj.linenumber + err.linenum()
            descr = err._descr
        obj.system.msg(
            'epydoc2stan2',
            '%s:%s epytext error %r' % (obj.fullName(), linenumber, descr))
    if errs and obj.fullName() not in obj.system.epytextproblems:
        obj.system.epytextproblems.append(obj.fullName())
        obj.system.msg('epydoc2stan',
                       'epytext error in %s'%(obj,), thresh=1)
        p = lambda m:obj.system.msg('epydoc2stan', m, thresh=2)
        for i, l in enumerate(obj.docstring.splitlines()):
            p("%4s"%(i+1)+' '+l)
        for err in errs:
            p(err)


def doc2stan(obj, summary=False, docstring=None):
    """Generate an HTML representation of a docstring"""
    if getattr(obj, 'parsed_docstring', None) is not None:
        r = html2stan(obj.parsed_docstring.to_html(_EpydocLinker(obj)))
        if getattr(obj, 'parsed_type', None) is not None:
            r = [r, ' (type: ', html2stan(obj.parsed_type.to_html(_EpydocLinker(obj))), ')']
        return r, []
    origobj = obj
    if isinstance(obj, model.Package):
        obj = obj.contents['__init__']
    if docstring is None:
        doc = None
        for source in obj.docsources():
            if source.docstring is not None:
                doc = source.docstring
                break
    else:
        source = obj
        doc = docstring
    if doc is None or not doc.strip():
        text = "Undocumented"
        subdocstrings = {}
        subcounts = {}
        for subob in origobj.contents.itervalues():
            k = subob.kind.lower()
            subcounts[k] = subcounts.get(k, 0) + 1
            if subob.docstring is not None:
                subdocstrings[k] = subdocstrings.get(k, 0) + 1
        if isinstance(origobj, model.Package):
            subcounts["module"] -= 1
        if subdocstrings:
            plurals = {'class':'classes'}
            text = "No %s docstring"%origobj.kind.lower()
            if summary:
                u = []
                for k in sorted(subcounts):
                    u.append("%s/%s %s"%(subdocstrings.get(k, 0), subcounts[k],
                                         plurals.get(k, k+'s')))
                text += '; ' + ', '.join(u) + " documented"
        if summary:
            return tags.span(class_="undocumented")(text), []
        else:
            return tags.div(class_="undocumented")(text), []
    if summary:
        # Use up to three first non-empty lines of doc string as summary.
        lines = itertools.dropwhile(lambda line: not line.strip(),
                                    doc.split('\n'))
        lines = itertools.takewhile(lambda line: line.strip(), lines)
        lines = [ line.strip() for line in lines ]
        if len(lines) > 3:
            return tags.span(class_="undocumented")('No summary'), []
        else:
            doc = ' '.join(lines)
    parse_docstring, e = get_parser(obj.system.options.docformat)
    if not parse_docstring:
        msg = 'Error trying to import %r parser:\n\n    %s: %s\n\nUsing plain text formatting only.'%(
            obj.system.options.docformat, e.__class__.__name__, e)
        obj.system.msg('epydoc2stan', msg, thresh=-1, once=True)
        return boringDocstring(doc, summary), []
    errs = []
    def crappit(): pass
    crappit.__doc__ = doc
    doc = inspect.getdoc(crappit)
    try:
        pdoc = parse_docstring(doc, errs)
    except Exception, e:
        errs = [e.__class__.__name__ +': ' + str(e)]
    if errs:
        reportErrors(source, errs)
        return boringDocstring(doc, summary), errs
    pdoc, fields = pdoc.split_fields()
    if pdoc is not None:
        try:
            crap = pdoc.to_html(_EpydocLinker(source))
        except Exception, e:
            reportErrors(source, [e.__class__.__name__ +': ' + str(e)])
            return (boringDocstring(doc, summary),
                    [e.__class__.__name__ +': ' + str(e)])
    else:
        crap = ''
    if isinstance(crap, unicode):
        crap = crap.encode('utf-8')
    if summary:
        if not crap:
            return (), []
        stan = html2stan(crap)
        if len(stan) == 1 and isinstance(stan[0], Tag) and stan[0].tagName == 'p':
            stan = stan[0].children
        s = tags.span(stan)
    else:
        if not crap and not fields:
            return (), []
        stan = html2stan(crap)
        s = tags.div(stan)
        fh = FieldHandler(obj)
        for field in fields:
            fh.handle(Field(field, obj))
        fh.resolve_types()
        s(fh.format())
    return s, []


field_name_to_human_name = {
    'ivar': 'Instance Variable',
    'cvar': 'Class Variable',
    'var': 'Variable',
    }


def extract_fields(obj):
    if isinstance(obj, model.Package):
        obj = obj.contents['__init__']
    if isinstance(obj, model.Function):
        return []
    doc = obj.docstring
    if doc is None or not doc.strip():
        return []
    parse_docstring, e = get_parser(obj.system.options.docformat)
    if not parse_docstring:
        return []
    def crappit(): pass
    crappit.__doc__ = doc
    doc = inspect.getdoc(crappit)
    try:
        pdoc = parse_docstring(doc, [])
    except Exception:
        return []
    pdoc, fields = pdoc.split_fields()
    if not fields:
        return []
    r = []
    types = {}
    for field in fields:
        if field.tag() == 'type':
            types[field.arg()] = field.body()
    for field in fields:
        if field.tag() in ['ivar', 'cvar', 'var']:
            attrobj = obj.system.Attribute(obj.system, field.arg(), None, obj)
            attrobj.parsed_docstring = field.body()
            attrobj.parsed_type = types.get(field.arg())
            attrobj.kind = field_name_to_human_name[field.tag()]
            r.append(attrobj)
    return r
