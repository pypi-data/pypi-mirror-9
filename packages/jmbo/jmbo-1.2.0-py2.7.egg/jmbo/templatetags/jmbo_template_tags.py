from datetime import datetime
import hashlib
import logging

from django import template
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.functional import Promise
from django.templatetags.cache import CacheNode
from django.template import resolve_variable
from django.template.base import VariableDoesNotExist
from django.core.cache import cache
from django.conf import settings

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def smart_url(url_callable, obj):
    return url_callable(obj)


@register.tag
def smart_query_string(parser, token):
    """
    Outputs current GET query string with additions appended.
    Additions are provided in token pairs.
    """
    args = token.split_contents()
    additions = args[1:]

    addition_pairs = []
    while additions:
        addition_pairs.append(additions[0:2])
        additions = additions[2:]

    return SmartQueryStringNode(addition_pairs)


class SmartQueryStringNode(template.Node):
    def __init__(self, addition_pairs):
        self.addition_pairs = []
        for key, value in addition_pairs:
            self.addition_pairs.append((
                template.Variable(key) if key else None,
                template.Variable(value) if value else None
            ))

    def render(self, context):
        q = dict([(k, v) for k, v in context['request'].GET.items()])
        for key, value in self.addition_pairs:
            if key:
                key = key.resolve(context)
                if value:
                    value = value.resolve(context)
                    q[key] = value
                else:
                    q.pop(key, None)
            qs = '&'.join(['%s=%s' % (k, v) for k, v in q.items()])
        return '?' + qs if len(q) else ''


@register.tag
def humanize_time_diff(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError, \
            "%s requires at least two argument" % bits[0]

    return HumanizeTimeDifference(*bits[1:])


class HumanizeTimeDifference(template.Node):
    """
    Adapted from Django Snippet 412

    Returns a humanized string representing time difference between now() and
    the input timestamp.

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """
    def __init__(self, date_obj, suffix, modifier=None):
        self.date_obj = template.Variable(date_obj)
        self.suffix = template.Variable(suffix)
        self.modifier = template.Variable(modifier) if modifier else None

    def humanize(self, date_obj, suffix):
        if date_obj:
            if isinstance(date_obj, datetime) and timezone.is_aware(date_obj):
                time_difference = timezone.now() - date_obj
            else:
                time_difference = datetime.now() - date_obj
            days = time_difference.days
            hours = time_difference.seconds / 3600
            minutes = time_difference.seconds % 3600 / 60
            seconds = time_difference.seconds % 3600 % 60

            if days > 0:
                if days == 1:
                    return _("Yesterday")
                else:
                    dt_str = _("Days")
                di = {'value': days, 'discriminant': dt_str, 'suffix': suffix}
                return _("%(value)s %(discriminant)s %(suffix)s") % di
            elif hours > 0:
                if hours == 1:
                    dt_str = _("Hour")
                else:
                    dt_str = _("Hours")
                di = {'value': hours, 'discriminant': dt_str, 'suffix': suffix}
                return _("%(value)s %(discriminant)s %(suffix)s") % di
            elif minutes > 0:
                if minutes == 1:
                    dt_str = _("Minute")
                else:
                    dt_str = _("Minutes")
                di = {
                    'value': minutes, 'discriminant': dt_str, 'suffix': suffix
                }
                return _("%(value)s %(discriminant)s %(suffix)s") % di
            elif seconds > 0:
                if seconds == 1:
                    dt_str = _("Second")
                else:
                    dt_str = _("Seconds")
                di = {
                    'value': seconds, 'discriminant': dt_str, 'suffix': suffix
                }
                return _("%(value)s %(discriminant)s %(suffix)s") % di
            elif seconds == 0:
                return _("Just Now")
        return ""

    def render(self, context):
        date_obj = self.date_obj.resolve(context)
        suffix = self.suffix.resolve(context)
        result = self.humanize(date_obj, suffix)
        if self.modifier:
            return getattr(result, self.modifier.resolve(context))()

        return result


@register.tag
def get_relation_list(parser, token):
    """Gets list of relations from object identified by a relation name.

    Syntax::

        {% get_relation_list [relation_name] for [object] as [varname] [direction] %}
    """
    tokens = token.contents.split()
    if len(tokens) not in (6, 7):
        raise template.TemplateSyntaxError(
            "%r tag requires 6 arguments" % tokens[0]
        )

    if tokens[2] != 'for':
        raise template.TemplateSyntaxError(
            "Third argument in %r tag must be 'for'" % tokens[0]
        )

    if tokens[4] != 'as':
        raise template.TemplateSyntaxError(
            "Fifth argument in %r tag must be 'as'" % tokens[0]
        )

    direction = 'forward'
    if len(tokens) == 7:
        direction = tokens[6]

    return RelationListNode(
        name=tokens[1], obj=tokens[3], as_var=tokens[5], direction=direction
    )


class RelationListNode(template.Node):

    def __init__(self, name, obj, as_var, direction='forward'):
        self.name = template.Variable(name)
        self.obj = template.Variable(obj)
        self.as_var = template.Variable(as_var)
        self.direction = template.Variable(direction)

    def render(self, context):
        name = self.name.resolve(context)
        obj = self.obj.resolve(context)
        as_var = self.as_var.resolve(context)
        try:
            direction = self.direction.resolve(context)
        except template.VariableDoesNotExist:
            direction = 'forward'
        context[as_var] = obj.get_related_items(name, direction)
        return ''


class JmboCacheNode(CacheNode):
    """Based on Django's default cache template tag. Add SITE_ID as implicit
    vary on parameter and allow unresolvable variables."""

    def __init__(self, *args, **kwargs):
        super(JmboCacheNode, self).__init__(*args, **kwargs)
        self.vary_on.append(str(settings.SITE_ID))

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise template.TemplateSyntaxError(
                '"cache" tag got an unknown variable: %r' % (
                    self.expire_time_var.var
                )
            )
        try:
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise template.TemplateSyntaxError(
                '"cache" tag got a non-integer timeout value: %r' % expire_time
            )

        # Build a unicode key for this fragment and all vary-on's.
        resolved = []
        for var in self.vary_on:
            try:
                r = resolve_variable(var, context)
            except VariableDoesNotExist:
                pass
            else:
                if isinstance(r, Promise):
                    r = unicode(r)
                resolved.append(r)

        args = hashlib.md5(u':'.join([urlquote(r) for r in resolved]))
        cache_key = 'template.cache.%s.%s' % (
            self.fragment_name, args.hexdigest()
        )
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache.set(cache_key, value, expire_time)

        # log if the cache is less than 4 bytes
        if len(value) <= 4:
            logger.error("JMBO Cache Error. Fragment Name: %s, Value: %s" % (
                self.fragment_name, value
            ))

        return value


@register.tag('jmbocache')
def do_jmbocache(parser, token):
    """Based on Django's default cache template tag"""
    nodelist = parser.parse(('endjmbocache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError(
            u"'%r' tag requires at least 2 arguments." % tokens[0]
        )
    return JmboCacheNode(nodelist, tokens[1], tokens[2], tokens[3:])
