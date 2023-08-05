from HTMLParser import HTMLParser
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


# URN schema for objects
#
URN_SCHEMA = "urn:pu.in:%(object_app)s:%(object_ctype)s:%(object_id)s"


def _class_implements(clazz, superclazz, check_self=True):

    well_does_it = False

    if check_self and clazz == superclazz:
        return True
    elif isinstance(superclazz, basestring) and superclazz in map(
            lambda x: "%s.%s" % (
                x.__module__.split('.')[0], x.__name__), clazz.__bases__):
        well_does_it = True
    elif superclazz in clazz.__bases__:
        well_does_it = True
    else:
        for base in clazz.__bases__:
            well_does_it = _class_implements(base, superclazz)
            if well_does_it:
                break

    return well_does_it


def implements(instance, clazz):

    """ Is it a bird? A plane? A clazz? """

    return _class_implements(instance.__class__, clazz)


def extends(clazz, otherclazz):

    """ Does the class extend the other one? """

    return _class_implements(clazz, otherclazz, check_self=False)


def object_to_urn(object):

    """ Create A URN for the given object """
    if not object:
        return ""

    app_label = getattr(object, "app_label", object._meta.app_label)
    ct_name = getattr(object, object.ct_name,
                      object.__class__.__name__.lower())

    return URN_SCHEMA % {'object_app': app_label,
                         'object_ctype': ct_name,
                         'object_id': object.id}


def urn_to_object(urn):

    """ Fetch the object for this URN. If not found, return None """

    parts = urn.split(":")

    ctype = ContentType.objects.get(app_label=parts[2], model=parts[3])

    try:
        return ctype.get_object_for_this_type(id=parts[4])
    except:
        return None


def get_object_by_ctype_id(ctype_id, _id, app_label=None):

    ctype = ContentType.objects.get(app_label=app_label, model=ctype_id)

    return ctype.get_object_for_this_type(id=_id)


def get_apps(name_filter=None):

    """ TODO: Django 1.7 has this call built in """

    _apps = {}

    for _app in settings.INSTALLED_APPS:
        if not name_filter or name_filter in _app:
            _apps[_app] = __import__(_app)

    return _apps


class HTMLTruncate(HTMLParser):

    """ Truncating class for html fragments """

    def __init__(self, limit):

        HTMLParser.__init__(self)

        self.limit = limit
        self.done = False
        self.count = 0
        self.truncated = []
        self.singles = ["br", "img", "hr"]
        self.queue = []

    def _flatten_attrs(self, attrs):

        if attrs:
            return " " + " ".join(
                ['%s="%s"' % (name, val) for name, val in attrs])
        else:
            return ""

    def handle_starttag(self, tag, attrs):

        if not self.done:

            if tag in self.singles:
                single_marker = "/"
            else:
                single_marker = ""

            self.queue.append(tag)
            self.truncated.append("<%s%s%s>" % (tag,
                                                self._flatten_attrs(attrs),
                                                single_marker))

    def handle_endtag(self, tag):

        if not self.done:
            if tag not in self.singles:
                self.truncated.append("</%s>" % tag)
            self.queue.pop()

    def handle_data(self, data):

        if not self.done:
            if self.count + len(data) > self.limit:
                self.done = True
                data = data[:(self.limit - self.count)]

            self.count += len(data)
            self.truncated.append(data)

    def truncate(self, text):

        self.done = False
        self.count = 0
        self.truncated = []
        self.queue = []

        self.feed(text)

        while self.queue:
            self.truncated.append("</%s>" % self.queue.pop())

        return "".join(self.truncated)
