#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import re
import json
import copy
import uuid
import types
import hashlib
import inspect
import functools

from . import legacy
from . import common
from . import defines
from . import exceptions

CREATION_COUNTER = 0
""" The global static creation counter value that
will be used to create an order in the declaration
of attributes for a set of classes """

SORT_MAP = {
    "1" : 1,
    "-1" : -1,
    "ascending" : 1,
    "descending" : -1,
}
""" The map associating the normalized (text) way of
representing sorting with the current infra-structure
number way of representing the same information """

SEQUENCE_TYPES = (list, tuple)
""" The sequence defining the various types that are
considered to be sequence based for python """

defines = defines

def to_find(find_s):
    find_t = type(find_s)
    if find_t == list: return find_s
    return [find_s]

def to_sort(sort_s):
    values = sort_s.split(":", 1)
    if len(values) == 1: values.append("descending")
    name, direction = values
    if name == "default": return None
    values[1] = SORT_MAP.get(direction, 1)
    return [tuple(values)]

ALIAS = {
    "filters" : "find_d",
    "filters[]" : "find_d",
    "filter_def" : "find_d",
    "filter_string" : "find_s",
    "order" : "sort",
    "start_record" : "skip",
    "number_records" : "limit"
}
""" The map containing the various attribute alias
between the normalized manned and the appier manner """

FIND_TYPES = dict(
    skip = int,
    limit = int,
    find_s = legacy.UNICODE,
    find_d = to_find,
    sort = to_sort,
    meta = bool
)
""" The map associating the various find fields with
their respective types """

def is_iterable(object):
    """
    Verifies if the provided object (value) is iterable
    meaning that the type of it is listed in a list of
    sequence based data types.

    :type object: Object
    :param object: The value that is going to be tested
    for iterable type.
    :rtype: bool
    :return: If the provided object represents an iterable
    object meaning that it belongs to sequence type.
    """

    return type(object) in defines.ITERABLES

def is_mobile(user_agent):
    """
    Verifies if the provided user agent string represent a
    mobile agent, for that a series of regular expressions
    are matched against the user agent string.

    :type user_agent: String
    :param user_agent: The string containing the user agent
    value that is going to be verified against a series of
    regular expressions for mobile verification.
    :rtype: bool
    :return: If the provided user agent string represents a
    mobile browser or a regular (desktop) one.
    """

    prefix = user_agent[:4]
    mobile = defines.MOBILE_REGEX.search(user_agent)
    mobile_prefix = defines.MOBILE_PREFIX_REGEX.search(prefix)
    is_mobile = True if mobile or mobile_prefix else False
    return is_mobile

def email_parts(base):
    """
    Unpacks the complete set of parts (name and email) from the
    provided generalized email string. The provided string may
    be a single email or the more complex form (eg: Name <email>).

    Note that the provided base argument may be a single string
    or a sequence of strings and the returning type will reflect
    that same provided parameter.

    :type base: String/List
    :param base: The base value that is going to be parsed as an
    email string or a sequence of such values.
    :rtype: Tuple/List
    :return: The resulting parsed tuple/tuples for the provided
    email strings, these tuples contain name and emails for each
    of the parsed values.
    """

    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [email_parts(base) for base in base]

    match = defines.EMAIL_REGEX.match(base)
    if not match: return (None, None)

    email = match.group("email_a") or match.group("email_b")
    name = match.group("name") or email

    return (name, email)

def email_mime(base):
    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return ["%s <%s>" % parts for parts in email_parts(base)]

    return "%s <%s>" % email_parts(base)

def email_name(base):
    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [email_base(base) for base in base]
    name, _email = email_parts(base)
    return name

def email_base(base):
    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [email_base(base) for base in base]
    _name, email = email_parts(base)
    return email

def request_json(request = None, encoding = "utf-8"):
    # retrieves the proper request object, either the provided
    # request or the default base request object and then in
    # case the the json data is already in the request properties
    # it is used (cached value) otherwise continues with the parse
    request = request or common.base().get_request()
    if "_data_j" in request.properties: return request.properties["_data_j"]

    # retrieves the current request data and tries to
    # "load" it as json data, in case it fails gracefully
    # handles the failure setting the value as an empty map
    data = request.data
    try:
        is_bytes = legacy.is_bytes(data)
        if is_bytes: data = data.decode(encoding)
        data_j = json.loads(data)
    except: data_j = {}
    request.properties["_data_j"] = data_j

    # returns the json data object to the caller method so that it
    # may be used as the parsed value (post information)
    return data_j

def get_object(object = None, alias = False, page = False, find = False, norm = True):
    # retrieves the base request object that is going to be used in
    # the construction of the object
    request = common.base().get_request()

    # verifies if the provided object is valid in such case creates
    # a copy of it and uses it as the base object for validation
    # otherwise used an empty map (form validation)
    object = object and copy.copy(object) or {}

    # retrieves the current request data and tries to
    # "load" it as json data, in case it fails gracefully
    # handles the failure setting the value as an empty map
    data_j = request_json()

    # uses all the values referencing data in the request to try
    # to populate the object this way it may be constructed using
    # any of theses strategies (easier for the developer)
    for name, value in data_j.items(): object[name] = value
    for name, value in request.files_s.items(): object[name] = value
    for name, value in request.post_s.items(): object[name] = value
    for name, value in request.params_s.items(): object[name] = value

    # in case the alias flag is set tries to resolve the attribute
    # alias and in case the find types are set converts the find
    # based attributes using the currently defined mapping map
    alias and resolve_alias(object)
    page and page_types(object)
    find and find_types(object)

    # in case the normalization flag is set runs the normalization
    # of the provided object so that sequences are properly handled
    # as define in the specification (this allows multiple references)
    norm and norm_object(object)

    # returns the constructed object to the caller method this object
    # should be a structured representation of the data in the request
    return object

def resolve_alias(object):
    for name, value in legacy.eager(object.items()):
        if not name in ALIAS: continue
        _alias = ALIAS[name]
        object[_alias] = value
        del object[name]

def page_types(object, size = 50):
    page = object.get("page", 1)
    size = object.get("size", size)
    sorter = object.get("sorter", None)
    direction = object.get("direction", "descending")
    page = int(page)
    size = int(size)
    offset = page - 1
    object["skip"] = offset * size
    object["limit"] = size
    if sorter: object["sort"] = "%s:%s" % (sorter, direction)

def find_types(object):
    for name, value in legacy.eager(object.items()):
        if not name in FIND_TYPES:
            del object[name]
            continue
        find_type = FIND_TYPES[name]
        object[name] = find_type(value)

def norm_object(object):
    # iterates over all the key value association in the
    # object, trying to find the ones that refer sequences
    # so that they may be normalized
    for name, value in object.items():
        # verifies if the current name references a sequence
        # and if that's not the case continues the loop trying
        # to find any other sequence based value
        if not name.endswith("[]"): continue

        # removes the current reference to the name as the value
        # is not in the valid structure and then normalizes the
        # name by removing the extra sequence indication value
        del object[name]
        name = name[:-2]

        # in case the current value is not valid (empty) the object
        # is set with an empty list for the current iteration as this
        # is considered to be the default value
        if not value: object[name] = []; continue

        # retrieves the normalized and linearized list of leafs
        # for the current value and ten verifies the size of each
        # of its values and uses it to measure the number of
        # dictionary elements that are going to be contained in
        # the sequence to be "generated", then uses this (size)
        # value to pre-generate the complete set of dictionaries
        leafs_l = leafs(value)
        first = leafs_l[0] if leafs_l else (None, [])
        _fqn, values = first
        size = len(values)
        list = [dict() for _index in range(size)]

        # sets the list of generates dictionaries in the object for
        # the newly normalized name of structure
        object[name] = list

        # iterates over the complete set of key value pairs in the
        # leafs list to gather the value into the various objects that
        # are contained in the sequence (normalization process)
        for _name, _value in leafs_l:
            for index in range(size):
                _object = list[index]
                _name_l = _name.split(".")
                set_object(_object, _name_l, _value[index])

def set_object(object, name_l, value):
    """
    Sets a composite value in an object, allowing for
    dynamic setting of random size key values.

    This method is useful for situations where one wants
    to set a value at a randomly defined depth inside
    an object without having to much work with the creation
    of the inner dictionaries.

    :type object: Dictionary
    :param object: The target object that is going to be
    changed and set with the target value.
    :type name_l: List
    :param name_l: The list of names that defined the fully
    qualified name to be used in the setting of the value
    for example path.to.end will be a three size list containing
    each of the partial names.
    :type value: Object
    :param value: The value that is going to be set in the
    defined target of the object.
    """

    # retrieves the first name in the names list this is the
    # value that is going to be used for the current iteration
    name = name_l[0]

    # in case the length of the current names list has reached
    # one this is the final iteration and so the value is set
    # at the current naming point
    if len(name_l) == 1: object[name] = value

    # otherwise this is a "normal" step and so a new map must
    # be created/retrieved and the iteration step should be
    # performed on this new map as it's set on the current naming
    # place (recursion step)
    else:
        map = object.get(name, {})
        object[name] = map
        set_object(map, name_l[1:], value)

def leafs(object):
    """
    Retrieves a list containing a series of tuples that
    each represent a leaf of the current object structure.

    A leaf is the last element of an object that is not a
    map, the other intermediary maps are considered to be
    trunks and should be percolated recursively.

    This is a recursive function that takes some memory for
    the construction of the list, and so should be used with
    the proper care to avoid bottlenecks.

    :type object: Dictionary
    :param object: The object for which the leafs list
    structure is meant to be retrieved.
    :rtype: List
    :return: The list of leaf node tuples for the provided
    object, as requested for each of the sequences.
    """

    # creates the list that will hold the various leaf nodes
    # "gathered" by the current recursion function
    leafs_l = []

    # iterates over all the key and value relations in the
    # object trying to find the leaf nodes (no map nodes)
    # creating a tuple of fqn (fully qualified name) and value
    for name, value in object.items():
        # retrieves the data type for the current value and
        # validation if it is a dictionary or any other type
        # in case it's a dictionary a new iteration step must
        # be performed retrieving the leafs of the value and
        # then incrementing the name with the current prefix
        value_t = type(value)
        if value_t == dict:
            _leafs = leafs(value)
            _leafs = [(name + "." + _name, value) for _name, value in _leafs]
            leafs_l.extend(_leafs)

        # otherwise this is a leaf node and so the leaf tuple
        # node must be constructed with the current value
        # (properly validated for sequence presence)
        else:
            value_t = type(value)
            if not value_t == list: value = [value]
            leafs_l.append((name, value))

    # returns the list of leaf nodes that was "just" created
    # to the caller method so that it may be used there
    return leafs_l

def gen_token():
    """
    Generates a random cryptographic ready token according
    to the framework specification, this is generated using
    a truly random uuid based seed and hashed using the
    sha256 hash digest.

    The resulting value is returned as an hexadecimal based
    string according to the standard.

    :rtype: String
    :return: The hexadecimal based string value
    """

    token_s = str(uuid.uuid4())
    token = hashlib.sha256(token_s).hexdigest()
    return token

def html_to_text(data):
    """
    Converts the provided html textual data into a plain text
    representation of it. This method uses a series of heuristics
    for this conversion, and such conversion should not be considered
    to be completely reliable.

    The current implementation is not memory or processor efficient
    and should be used carefully to avoid performance problems.

    :type data: String
    :param data: The html string of text that is going to be used for
    the conversion into the plain text representation.
    :rtype: String
    :return: The approximate plain text representation to the provided
    html contents.
    """

    data = data.strip()
    data = data.replace("\n", "\r")

    data = data.replace("&copy;", "Copyright")
    data = data.replace("&middot;", "-")

    result = re.findall(defines.BODY_REGEX, data)
    data = result[0]

    data = defines.TAG_REGEX.sub("", data)

    valid = []
    lines = data.splitlines(False)
    for line in lines:
        line = line.strip()
        if not line: continue
        valid.append(line)

    data = "\n".join(valid)
    data = data.replace("\n.", ".")
    return data

def camel_to_underscore(camel):
    """
    Converts the provided camel cased based value into
    a normalized underscore based string.

    This is useful as most of the python string standards
    are compliant with the underscore strategy.

    :type camel: String
    :param camel: The camel cased string that is going to be
    converted into an underscore based string.
    :rtype: String
    :return The underscore based string resulting from the
    conversion of the provided camel cased one.
    """

    values = []
    camel_l = len(camel)

    for index in range(camel_l):
        char = camel[index]
        is_upper = char.isupper()

        if is_upper and not index == 0: values.append("_")
        values.append(char)

    return "".join(values).lower()

def camel_to_readable(camel):
    """
    Converts the given camel cased oriented string value
    into a readable one meaning that the returned value
    is a set of strings separated by spaces.

    This method may be used to convert class names into
    something that is readable by an end user.

    :type camel: String
    :param camel: The camel case string value that is going
    to be used in the conversion into a readable string.
    :rtype: String
    :return: The final human readable string that may be
    used to display a value to an end user.
    """

    underscore = camel_to_underscore(camel)
    parts = underscore.split("_")
    parts[0] = parts[0].title()
    return " ".join(parts)

def quote(value, *args, **kwargs):
    """
    Quotes the passed value according to the defined
    standard for url escaping, the value is first encoded
    into the expected utf-8 encoding as defined by standard.

    This method should be used instead of a direct call to
    the equivalent call in the url library.

    :type value: String
    :param value: The string value that is going to be quoted
    according to the url escaping scheme.
    :rtype: String
    :return: The quoted value according to the url scheme this
    value may be safely used in urls.
    """

    is_unicode = type(value) == legacy.UNICODE
    if is_unicode: value = value.encode("utf-8")
    return legacy.quote(value, *args, **kwargs)

def unquote(value, *args, **kwargs):
    """
    Unquotes the provided value according to the url scheme
    the resulting value should be an unicode string representing
    the same value, the intermediary string value from the decoding
    should be an utf-8 based value.

    This method should be used instead of a direct call to
    the equivalent call in the url library.

    :type value: String
    :param value: The string value that is going to be unquoted
    according to the url escaping scheme.
    :rtype: String
    :return: The unquoted value extracted as an unicode
    string that the represents the same value.
    """

    value = legacy.unquote(value, *args, **kwargs)
    is_bytes = type(value) == legacy.BYTES
    if is_bytes: value = value.decode("utf-8")
    return value

def base_name(name, suffix = "_controller"):
    """
    Retrieves the base name of a class name that contains
    a suffix (eg: controller) the resulting value is the
    underscore version of the name without the suffix.

    This method provides an easy way to expose class names
    in external environments.

    :type name: String
    :param name: The name from which the base name will be
    extracted and treated.
    :type suffix: String
    :param suffix: The optional suffix value that if sent will
    be removed from the last part of the name string.
    :rtype: String
    :return: The resulting base name for the provided name, treated
    and with the suffix removed (in case it exists).
    """

    suffix_l = len(suffix)
    name = camel_to_underscore(name)
    if name.endswith(suffix): name = name[:suffix_l * -1]
    return name

def base_name_m(name, suffixes = ("_controller", "_part", "_app")):
    """
    Multiple iteration version of the base name function that provides
    a simple strategy for the retrieval of a "base name" without the
    complete set of provided suffixes attached to the value.

    :type name: String
    :param name: The name from which the base name will be
    extracted and treated, with multiple value strategy.
    :type suffixes: List/Tuple
    :param suffixes: The complete set of suffixes that are going
    to be removed from the provided value creating the base name.
    :rtype: String
    :return: The resulting base name for the provided name, treated
    and without the complete set of provided suffixes.
    """

    for suffix in suffixes: name = base_name(name, suffix = suffix)
    return name

def parse_multipart(data, boundary):
    """
    Parses the provided data buffer as a set of multipart data
    the content type is not verified inside this method.

    The function returns a tuple containing both a map of "basic"
    form parameters and a map containing the set of file tuples.

    :type data: String
    :param data: The string containing the complete set of data
    that is going to be processed as multipart.
    :type boundary: String
    :param boundary: The string containing the basic boundary header
    value, should be provided from the caller function.
    :rtype: Tuple
    :return: A tuple containing both the map of post attributes and
    the map of file attributes.
    """

    post = dict()
    files = dict()

    boundary = boundary.strip()
    boundary_base = "--" + boundary[9:]
    boundary_value = legacy.bytes(boundary_base + "\r\n")
    boundary_extra = legacy.bytes(boundary_base + "--" + "\r\n")
    boundary_extra_l = len(boundary_extra)
    parts = data.split(boundary_value)
    parts[-1] = parts[-1][:boundary_extra_l * -1]

    for part in parts:
        if not part: continue
        part_s = part.split(b"\r\n\r\n", 1)
        headers = part_s[0]
        if len(part_s) > 1: contents = part_s[1]
        else: contents = None

        # strips the current headers string and then splits it around
        # the various lines that define the various headers
        headers_data = headers.strip()
        headers_lines = headers_data.split(b"\r\n")

        # creates the initial headers map of the headers that contains
        # the association between the byte based key and the data value
        # then retrieves the tuple of values and resets the map as it's
        # going to be changed and normalized with the new values
        headers = dict([line.split(b":", 1) for line in headers_lines])
        headers_t = legacy.eager(headers.items())
        headers.clear()

        # runs the normalization process using the header tuples, this
        # should create a map of headers with the key as a normal string
        # and the values encoded as byte based strings (contain data)
        # note that the headers are defined
        for key, value in headers_t:
            key = legacy.str(key).lower()
            value = value.strip()
            headers[key] = value

        # tries to retrieve the content disposition header for the current
        # part and in case there's none it's not possible to process the
        # current part (this header is considered required)
        disposition = headers.get("content-disposition", None)
        if not disposition: continue

        # creates the dictionary that will hold the various parts of the
        # content disposition header that are going to be extracted for
        # latter processing, this is required to make some decisions on
        # the type of part that is currently being processed
        parts = dict()
        parts_data = disposition.split(b";")
        for value in parts_data:
            value_s = value.split(b"=", 1)
            key = legacy.str(value_s[0]).strip().lower()
            if len(value_s) > 1: value = value_s[1].strip()
            else: value = None
            parts[key] = value

        # retrieves the various characteristics values from the headers
        # and from the content disposition of the current part, these
        # values are going to be used to decide on whether the current
        # part is a file or a normal key value attribute
        content_type = headers.get("content-type", None)
        name = parts.get("name", b"\"undefined\"")[1:-1]
        filename = parts.get("filename", b"")[1:-1]

        # decodes the various content disposition values into an unicode
        # based string so that may be latter be used safely inside the
        # application environment(as expected by the current structure)
        if content_type: content_type = content_type.decode("utf-8")
        name = name.decode("utf-8")
        filename = filename.decode("utf-8")

        # in case the currently discovered contents are valid they
        # must be stripped from the last two bytes so that the real
        # value is retrieved from the provided contents
        contents = contents if contents == None else contents[:-2]

        # verifies if the file name is included in the parts unpacked
        # from the content type in case it does this is considered to be
        # file part otherwise it's a normal key value part
        if "filename" in parts: is_file = True
        else: is_file = False

        if is_file:
            target = files
            file_tuple = (filename, content_type, contents)
            value = FileTuple(file_tuple)
        else:
            target = post
            value = contents if contents == None else contents.decode("utf-8")

        sequence = target.get(name, [])
        sequence.append(value)
        target[name] = sequence

    return (post, files)

def decode_params(params):
    """
    Decodes the complete set of parameters defined in the
    provided map so that all of keys and values are created
    as unicode strings instead of utf-8 based strings.

    This method's execution is mandatory on the retrieval of
    the parameters from the sent data.

    :type params: Dictionary
    :param params: The map containing the encoded set of values
    that are going to be decoded from the utf-8 form.
    :rtype: Dictionary
    :return: The decoded map meaning that all the keys and values
    are in the unicode form instead of the string form.
    """

    # creates the dictionary that will hold the processed/decoded
    # sequences of parameters created from the provided (and original)
    # map of encoded parameters (raw values)
    _params = dict()

    for key, value in params.items():
        items = []
        for item in value:
            is_bytes = legacy.is_bytes(item)
            if is_bytes: item = item.decode("utf-8")
            items.append(item)
        is_bytes = legacy.is_bytes(key)
        if is_bytes: key = key.decode("utf-8")
        _params[key] = items

    return _params

def load_form(form):
    # creates the map that is going to hold the "structured"
    # version of the form with key value associations
    form_s = {}

    # iterates over all the form items to parse their values
    # and populate the form structured version of it, note that
    # for the sake of parsing the order of the elements in the
    # form is relevant, in case there's multiple values for the
    # same name they are considered as a list, otherwise they are
    # considered as a single value
    for name in form:
        # retrieves the value (as a list) for the current name, then
        # in case the sequence is larger than one element sets it,
        # otherwise retrieves and sets the value as the first element
        value = form[name]
        value = value[0] if len(value) == 1 else value

        # splits the complete name into its various components
        # and retrieves both the final (last) element and the
        # various partial elements from it
        names = name.split(".")
        final = names[-1]
        partials = names[:-1]

        # sets the initial "struct" reference as the form structured
        # that has just been created (initial structure for iteration)
        # then starts the iteration to retrieve or create the various
        # intermediate structures
        struct = form_s
        for _name in partials:
            _struct = struct.get(_name, {})
            struct[_name] = _struct
            struct = _struct

        # sets the current value in the currently loaded "struct" element
        # so that the reference gets properly updated
        struct[final] = value

    # retrieves the final "normalized" form structure containing
    # a series of chained maps resulting from the parsing of the
    # linear version of the attribute names
    return form_s

def check_login(token = None, request = None):
    # retrieves the data type of the token and creates the
    # tokens sequence value taking into account its type
    token_type = type(token)
    if token_type in SEQUENCE_TYPES: tokens = token
    else: tokens = (token,)

    # in case the username value is set in session and there's
    # no token to be validated returns valid and in case the
    # wildcard token is set also returns valid because this
    # token provides access to all features
    if "username" in request.session and not token: return True
    if "*" in request.session.get("tokens", []): return True

    # retrieves the current set of tokens set in session and
    # then iterates over the current tokens to be validated
    # to check if all of them are currently set in session
    tokens_s = request.session.get("tokens", [])
    for token in tokens:
        if not token in tokens_s: return False

    # returns the default value as valid because if all the
    # validation procedures have passed the check is valid
    return True

def ensure_login(self, function, token = None, request = None):
    request = request or self.request
    is_auth = "username" in request.session
    if not is_auth: raise exceptions.AppierException(
        message = "User not authenticated",
        code = 403
    )

    if not token: return
    if "*" in self.session.get("tokens", []): return

    tokens_s = self.session.get("tokens", [])
    if not token in tokens_s: raise exceptions.AppierException(
        message = "Not enough permissions",
        code = 403
    )

def private(function):

    @functools.wraps(function)
    def _private(self, *args, **kwargs):
        ensure = kwargs.get("ensure", True)
        request = kwargs.get("request", self.request)
        if ensure: ensure_login(self, function, request = request)
        sanitize(function, kwargs)
        return function(self, *args, **kwargs)

    return _private

def ensure(token = None):

    def decorator(function):
        @functools.wraps(function)
        def interceptor(self, *args, **kwargs):
            ensure = kwargs.get("ensure", True)
            request = kwargs.get("request", self.request)
            if ensure: ensure_login(
                self,
                function,
                token = token,
                request = request
            )
            sanitize(function, kwargs)
            return function(self, *args, **kwargs)

        return interceptor

    return decorator

def delayed(function):

    @functools.wraps(function)
    def _delayed(self, *args, **kwargs):
        _args = [self] + list(args)
        return self.owner.delay(function, _args, kwargs)

    return _delayed

def route(url, method = "GET", async = False, json = False):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_route(
            method,
            url,
            function,
            async = async,
            json = json
        )
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        route = (url, method, async, json)
        if not hasattr(function, "_routes"): function._routes = []
        function._routes.append(route)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1

    return decorator

def error_handler(code):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_error(code, function)
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        error = (code,)
        if not hasattr(function, "_errors"): function._errors = []
        function._errors.append(error)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1
        return function

    return decorator

def exception_handler(exception):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_exception(exception, function)
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        _exception = (exception,)
        if not hasattr(function, "_exceptions"): function._exceptions = []
        function._exceptions.append(_exception)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1
        return function

    return decorator

def is_detached(function):
    """
    Verifies if the provided function value is considered to be
    a detached method from a class, this is valid for situations
    where the type of the value is a function and there's a reference
    to the parent class of definition.

    This method is not completely safe as it relies on the fact that
    by convention the first argument of a "future" method is the "self"
    one, meaning that a "normal function" would be detected as a
    method if the first argument of it is named self.

    :type function: Function
    :param function: The function value that is going to be evaluated
    for the presence of a detached method.
    :rtype: bool
    :return: If the provided function value refers a detached method
    of a certain class.
    """

    # verifies if the provided value is a valid function type
    # an in case it's not it's considered to not be a detached
    is_function = isinstance(function, types.FunctionType)
    if not is_function: return False

    # retrieves the function's specification (should include arguments)
    # and then verifies that they are valid and that at least one valid
    # argument exists for the specification (as required by methods)
    spec = inspect.getargspec(function)
    if not spec: return False
    if not spec.args: return False

    # verifies that the name of the first argument of the function is the
    # the instance one, if that's the case this should be a detached method
    # that is currently being identified as a function
    return spec.args[0] == "self"

def sanitize(function, kwargs):
    removal = []
    method_a = inspect.getargspec(function)[0]
    for name in kwargs:
        if name in method_a: continue
        removal.append(name)
    for name in removal: del kwargs[name]

class FileTuple(tuple):
    """
    Tuple class (inherits from tuple) that represents
    the name, content type and (data) contents of a file
    in the context of the appier infra-structure.

    This class shares many of the signature with the
    typical python class interface.
    """

    def read(self, count = None):
        contents = self[2]
        return contents

    def save(self, path):
        contents = self[2]
        file = open(path, "wb")
        try: file.write(contents)
        finally: file.close()
