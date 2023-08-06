from __future__ import absolute_import
from .const import SCOPE_SEPARATOR
from .errs import CycleDetectionError
import six
import imp
import sys
import datetime
import re

#TODO: accept varg
def scope_compose(scope, name, sep=SCOPE_SEPARATOR):
    """ compose a new scope

    :param str scope: current scope
    :param str name: name of next level in scope
    :return the composed scope
    """

    if name == None:
        new_scope = scope
    else:
        new_scope = scope if scope else name

    if scope and name:
        new_scope = scope + sep + name

    return new_scope

def scope_split(scope, sep=SCOPE_SEPARATOR):
    """ split a scope into names
    
    :param str scope: scope to be splitted
    :return: list of str for scope names
    """

    return scope.split(sep) if scope else [None]


class ScopeDict(dict):
    """ ScopeDict
    """
    def __init__(self, *a, **k):
        self.__sep = SCOPE_SEPARATOR
        super(ScopeDict, self).__init__(*a, **k)

    @property
    def sep(self):
        """ separator property
        """
        raise TypeError('sep property is write-only')

    @sep.setter
    def  sep(self, sep):
        self.__sep = sep

    def __getitem__(self, *keys):
        """ to access an obj with key: 'n!##!m...!##!z', caller can pass as key:
        - n!##!m...!##!z
        - n, m, ..., z
        - z

        :param dict keys: keys to access via scopes.
        """
        k = six.moves.reduce(lambda k1, k2: scope_compose(k1, k2, sep=self.__sep), keys[0]) if isinstance(keys[0], tuple) else keys[0]
        try:
            return super(ScopeDict, self).__getitem__(k)
        except KeyError as e:
            ret = []
            for ik in self.keys():
                if ik.endswith(k):
                    ret.append(ik)
            if len(ret) == 1:
                return super(ScopeDict, self).__getitem__(ret[0])
            elif len(ret) > 1:
                raise ValueError('Multiple occurrence of key: {0}'.format(k))

            raise e


class CycleGuard(object):
    """ Guard for cycle detection
    """

    def __init__(self, identity_hook=id):
        self.__visited = []
        self.__hook = identity_hook

    def update(self, obj):
        i = self.__hook(obj)
        if i in self.__visited:
            raise CycleDetectionError('Cycle detected: {0}'.format(obj.__repr__()))
        self.__visited.append(i)


class FixedTZ(datetime.tzinfo):
    """ tzinfo implementation without consideration of
    daylight-saving-time.
    """

    def __init__(self, h=0, m=0):
        self.__offset = datetime.timedelta(hours=h, minutes=m)

    def utcoffset(self, dt):
        return self.__offset + self.dst(dt)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

_iso8601_fmt = re.compile(''.join([
    '(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})', # YYYY-MM-DD
    'T', # T
    '(?P<hour>\d{2}):(?P<minute>\d{2})(:(?P<second>\d{1,2}))?', # hh:mm:ss
    '(?P<tz>Z|[+-]\d{2}:\d{2})?' # Z or +/-hh:mm
]))
_iso8601_fmt_date = re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})') # YYYY-MM-DD

def from_iso8601(s):
    """ convert iso8601 string to datetime object.
    refer to http://xml2rfc.ietf.org/public/rfc/html/rfc3339.html#anchor14
    for details.

    :param str s: time in ISO-8601
    :rtype: datetime.datetime
    """
    m = _iso8601_fmt.match(s)
    if not m:
        m = _iso8601_fmt_date.match(s)

    if not m:
        raise ValueError('not a valid iso 8601 format string:[{0}]'.format(s))

    g = m.groupdict()

    def _default_zero(key):
        v = g.get(key, None)
        return int(v) if v else 0

    def _default_none(key):
        v = g.get(key, None)
        return int(v) if v else None

    year = _default_zero('year')
    month = _default_zero('month')
    day = _default_zero('day')
    hour = _default_none('hour')
    minute = _default_none('minute')
    second = _default_none('second')
    tz_s = g.get('tz')

    if not (year and month and day):
        raise ValueError('missing y-m-d: [{0}]'.format(s))

    # only date part, time part is none
    if hour == None and minute == None and second == None:
        return datetime.datetime(year, month, day)

    # prepare tz info
    tz = None
    if tz_s:
        if not (hour and minute):
            raise ValueError('missing h:m when tzinfo is provided: [{0}]'.format(s))

        negtive = hh = mm = 0

        if tz_s != 'Z':
            negtive = -1 if tz_s[0] == '-' else 1
            hh = int(tz_s[1:3])
            mm = int(tz_s[4:6]) if len(tz_s) > 5 else 0

        tz = FixedTZ(h=hh*negtive, m=mm*negtive)

    return datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour or 0,
        minute=minute or 0,
        second=second or 0,
        tzinfo=tz
    )

def import_string(name):
    """ import module
    """
    mod = fp = None

    # code below, please refer to 
    #   https://docs.python.org/2/library/imp.html
    # for details
    try:
        return sys.modules[name]
    except KeyError:
        pass

    try:
        fp, pathname, desc = imp.find_module(name)
        mod = imp.load_module(name, fp, pathname, desc)
    except ImportError:
        mod = None 
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

    return mod

def jp_compose(s, base=None):
    """ append/encode a string to json-pointer
    """
    if s == None:
        return base

    ss = [s] if isinstance(s, six.string_types) else s
    ss = [s.replace('~', '~0').replace('/', '~1') for s in ss]
    if base:
        ss.insert(0, base)
    return '/'.join(ss)

def jp_split(s):
    """ split/decode a string from json-pointer
    """
    if s == '' or s == None:
        return []

    def _decode(s):
        s = s.replace('~1', '/')
        return s.replace('~0', '~')

    return [_decode(ss) for ss in s.split('/')]

def jr_split(s):
    """ split a json-reference into (url, json-pointer)
    """
    p = six.moves.urllib.parse.urlparse(s)
    return (
        normalize_url(six.moves.urllib.parse.urlunparse(p[:5]+('',))),
        '#'+p.fragment if p.fragment else '#'
    )

def deref(obj):
    """ dereference $ref
    """
    cur, guard = obj, CycleGuard()
    while cur and getattr(cur, 'ref_obj', None) != None:
        # cycle guard
        guard.update(cur)

        cur = cur.ref_obj
    return cur

def get_dict_as_tuple(d):
    """ get the first item in dict,
    and return it as tuple.
    """
    for k, v in six.iteritems(d):
        return k, v
    return None

def nv_tuple_list_replace(l, v):
    """ replace a tuple in a tuple list
    """
    _found = False
    for i, x in enumerate(l):
        if x[0] == v[0]:
            l[i] = v
            _found = True

    if not _found:
        l.append(v)

def path2url(p):
    """ Return file:// URL from a filename.
    """
    return six.moves.urllib.parse.urljoin(
        'file:', six.moves.urllib.request.pathname2url(p)
    )

def normalize_url(url):
    """ Normalize url
    """
    if not url:
        return url

    p = six.moves.urllib.parse.urlparse(url)
    if p.scheme == '':
        if p.netloc == '' and p.path != '':
            # it should be a file path
            url = path2url(url)
        else:
            raise ValueError('url should be a http-url or file path -- ' + url)

    return url

def normalize_jr(jr, prefix, url=None):
    """ normalize JSON reference, also fix
    implicit reference of JSON pointer.
    input:
    - User
    - #/definitions/User
    - http://test.com/swagger.json#/definitions/User
    output:
    - http://test.com/swagger.json#/definitions/User
    """

    if jr == None:
        return jr

    p = six.moves.urllib.parse.urlparse(jr)
    if p.scheme != '':
        return jr

    # it's a JSON reference without url

    # fix implicit reference
    jr = jp_compose(jr, base=prefix) if jr.find('#') == -1 else jr

    # prepend url
    if url:
        p = six.moves.urllib.parse.urlparse(url)
        # remember to remove the heading '#'
        jr = six.moves.urllib.parse.urlunparse(p[:5]+(jr[1:],))

    return jr

def is_file_url(url):
    return url.startswith('file://')

def get_swagger_version(obj):
    """ get swagger version from loaded json """

    if isinstance(obj, dict):
        if 'swaggerVersion' in obj:
            return obj['swaggerVersion']
        elif 'swagger' in obj:
            return obj['swagger']
        return None
    else:
        # should be an instance of BaseObj
        return obj.swaggerVersion if hasattr(obj, 'swaggerVersion') else obj.swagger

def walk(start, ofn, cyc=None):
    """ Non recursive DFS to detect cycles

    :param start: start vertex in graph
    :param ofn: function to get the list of outgoing edges of a vertex
    :param cyc: list of existing cycles, cycles are represented in a list started with minimum vertex.
    :return: cycles
    :rtype: list of lists
    """
    ctx, stk = {}, [start]
    cyc = [] if cyc == None else cyc

    while len(stk):
        top = stk[-1]

        if top not in ctx:
            ctx.update({top:list(ofn(top))})

        if len(ctx[top]):
            n = ctx[top][0]
            if n in stk:
                # cycles found,
                # normalize the representation of cycles,
                # start from the smallest vertex, ex.
                # 4 -> 5 -> 2 -> 7 -> 9 would produce
                # (2, 7, 9, 4, 5)
                nc = stk[stk.index(n):]
                ni = nc.index(min(nc))
                nc = nc[ni:] + nc[:ni] + [min(nc)]
                if nc not in cyc:
                    cyc.append(nc)

                ctx[top].pop(0)
            else:
                stk.append(n)
        else:
            ctx.pop(top)
            stk.pop()
            if len(stk):
                ctx[stk[-1]].remove(top)

    return cyc


