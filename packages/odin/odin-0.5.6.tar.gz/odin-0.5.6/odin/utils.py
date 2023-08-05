# -*- coding: utf-8 -*-
import re

_CAMEL_CASE_RE = re.compile(r'[A-Z]')
_LOWER_UNDERSCORE_CASE_RE = re.compile(r'_([a-z])')
_LOWER_DASH_CASE_RE = re.compile(r'-([a-z])')


def camel_to_lower_separated(s, sep):
    """
    Convert camel case representation into lower separated case ie:

      backgroundColor -> background_color

    Note any separator at the start or end is stripped.

    """
    return _CAMEL_CASE_RE.sub(lambda m: sep + m.group(0).lower(), s).strip(sep)


def camel_to_lower_underscore(s):
    """
    Convert camel case to lower underscore case.

        backgroundColor -> background_color
    """
    return camel_to_lower_separated(s, '_')


def camel_to_lower_dash(s):
    """
    Convert camel case to lower dash case.

      backgroundColor -> background-color
    """
    return camel_to_lower_separated(s, '-')


def lower_underscore_to_camel(value):
    """
    Convert lower underscore case to camel case

      background_color -> backgroundColor
    """
    return _LOWER_UNDERSCORE_CASE_RE.sub(
        lambda m: m.group(1).upper(),
        value.lower()
    )


def lower_dash_to_camel(value):
    """
    Convert lower dash case to camel case

      background-color -> backgroundColor
    """
    return _LOWER_DASH_CASE_RE.sub(
        lambda m: m.group(1).upper(),
        value.lower()
    )


class cached_property(object):
    """
    Acts like a standard class `property` except return values cached.
    """
    @staticmethod
    def clear_caches(instance):
        instance._cache = {}

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.__module__ = func.__module__

    def __get__(self, instance, owner):
        try:
            value = instance._cache[self.__name__]
        except (KeyError, AttributeError):
            value = self.func(instance)
            try:
                cache = instance._cache
            except AttributeError:
                cache = instance._cache = {}
            cache[self.__name__] = value
        return value


def field_iter(resource, include_virtual=True):
    """
    Return an iterator that yields fields from a resource.

    :param resource: Resource to iterate over.
    :param include_virtual: Include virtual fields.
    :returns: an iterator that returns fields.

    """
    if include_virtual:
        return iter(resource._meta.all_fields)
    else:
        return iter(resource._meta.fields)


def field_iter_items(resource, fields=None):
    """
    Return an iterator that yields fields and their values from a resource.

    :param resource: Resource to iterate over.
    :param fields: Fields to use; if :const:`None` defaults to all of the resources fields.
    :returns: an iterator that returns (field, value) tuples.

    """
    if fields is None:
        fields = resource._meta.all_fields
    for f in fields:
        yield f, f.prepare(f.value_from_object(resource))


def virtual_field_iter_items(resource):
    """
    Return an iterator that yields virtual fields and their values from a resource.

    :param resource: Resource to iterate over.
    :returns: an iterator that returns (field, value) tuples.

    """
    return field_iter_items(resource, resource._meta.virtual_fields)


def attribute_field_iter_items(resource):
    """
    Return an iterator that yields fields and their values from a resource that have the attribute flag set.

    :param resource: Resource to iterate over.
    :returns: an iterator that returns (field, value) tuples.

    :note::
        This iterator is designed for codecs that have a distinction between attribute and element fields (eg XML).

    """
    return field_iter_items(resource, resource._meta.attribute_fields)


def element_field_iter_items(resource):
    """
    Return an iterator that yields fields and their values from a resource that do not have the attribute flag set.

    :param resource: Resource to iterate over.
    :returns: an iterator that returns (field, value) tuples.

    :note::
        This iterator is designed for codecs that have a distinction between attribute and element fields (eg XML).

    """
    return field_iter_items(resource, resource._meta.element_fields)


def extract_fields_from_dict(d, resource):
    """
    Extract values from a dict that are defined on a resource.

    Fields that are not found will not be included in the output dict.

    :param d: the source dictionary.
    :param resource: the resource that provides the fields.
    :returns: a dictionary of the resource fields that where found in the dict.

    """
    return {f.name: d[f.name] for f in field_iter(resource) if f.name in d}
