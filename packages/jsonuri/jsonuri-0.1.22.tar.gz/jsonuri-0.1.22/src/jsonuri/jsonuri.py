__author__ = 'guilherme'

import urllib
import urllib.parse


def _encode_uri_component(e):
    """Converts a string into a URI encoded string

    :param e: String to be encoded
    :return: URI encoded string
    """
    revert = {'%21': '!', '%2A': '*', '%26': '&', '%27': "'", '%28': '(', '%29': ')'}

    pairs = {v: k for k, v in revert.items()}

    ec = urllib.parse.quote(str(e))

    for k, v in pairs.items():

        if k in ec:
            ec = ec.replace(k, v)

    return ec


def _decode_uri_param(param):
    """Converts `param` to a Python dictionary

    :param is a key=value URI parameter string
    :return Dictionary with `key` and `value` pair

    """
    values = param.split("=", 1)

    try:
        pair = dict(key=values[0], value=values[1])
    except IndexError:
        raise ValueError("Malformed string: `{0}`".format(param))

    return pair


def __serialize(data, encode=True, prefix="", call=0):
    """Serializes a python dictionary or list into a URI parameters' string

    :param data: Python dictionary or list to serialize
    :param encode: If True, the serialized string will be encoded with the urllib.parse.quote_plus method
    :param prefix: Prefix of partially serialized string, in recursive call
    :param call: Recursive function call index (first, second, third time...
    :return: Serialized data string, optionally encoded

  """
    params = []

    if type(data) is list:

        for ik in range(0, len(data)):
            params.append(__serialize(data[ik], encode, ''.join([prefix, "[", str(ik), "]"]), call + 1))

    elif type(data) is dict:

        for k in data:
            sep = ""

            if prefix:
                if prefix[-1] != "]":
                    sep = ":"

            params.append(__serialize(data[k], encode, ''.join([prefix, sep, k]), call + 1))
    else:

        params.append(''.join([prefix, "=", _encode_uri_component(data)]))

    if call == 0 and encode is True:

        for i in range(0, len(params)):
            params[i] = urllib.parse.quote_plus(params[i])

    return '&'.join(params)


def serialize(data, encode=True):

    """Serializes a python dictionary or list into a URI parameters' string

    :param data: Python dictionary or list to serialize
    :param encode: If True, the serialized string will be encoded with the urllib.parse.quote_plus method
    :return: Serialized data string, encoded if `encode` is `True`


    >>> import json
    >>> import urllib.parse
    >>> serialize(json.loads('{"age": "31", "name": "John"}'))
    'age%3D31%26name%3DJohn'
    >>> serialize(json.loads('{"age": "31", "name": "John"}'), False)
    'age=31&name=John'

    """

    return __serialize(data, encode, "", 0)


def __map_object_key(key, value, object):
    """Handles deserialization by mapping a key to its value and adding it to the object parameter, which is
    assumed to be a Python dictionary.

    :param key: Key of URI parameter
    :param value: Remaining URI string after the assignment sign
    :param object: Python dictionary to store mapped value of key
    """

    index_of_object_sep = key.find(":")
    index_of_array = key.find("[")

    #`:` comes first
    if (index_of_object_sep != -1) and (index_of_object_sep < index_of_array or index_of_array == -1):

        extracted_key = key[0:index_of_object_sep]
        remaining_key = key[index_of_object_sep + 1:]

        if extracted_key not in object:
            object[extracted_key] = dict()

        if not remaining_key:
            object[extracted_key] = value
        else:
            __map_object_key(remaining_key, value, object[extracted_key])

    #`[` comes first
    elif (index_of_array != -1) and (index_of_array < index_of_object_sep or index_of_object_sep == -1):

        extracted_key = key[0:index_of_array]
        remaining_key = key[key.find("]") + 1:]

        if extracted_key not in object:
            object[extracted_key] = []

        index = int(key[index_of_array + 1:key.find("]")])

        #add list element
        while index + 1 > len(object[extracted_key]):
            object[extracted_key].append(dict())

        if not remaining_key:
            object[extracted_key][index] = value
        else:
            __map_object_key(remaining_key, value, object[extracted_key][index])

    else:

        object[key] = value


def __deserialize(string, decode_twice, object, call):
    """Converts a URI parameters' string into a python dictionary

    :param string: Serialized URI parameters string to deserialize
    :param object: Python dictionary to store deserialized data
    :param call: Recursive function call index (first, second, third time...)

    """

    if call == 0:

        if decode_twice:
            tmp = urllib.parse.unquote(string)
        else:
            tmp = string

        strings = urllib.parse.unquote_plus(tmp).split("&")

        for i in range(0, len(strings)):
            strings[i] = urllib.parse.unquote_plus(strings[i])

        for i in range(0, len(strings)):
            __deserialize(strings[i], decode_twice, object, call + 1)

    else:
        pair = _decode_uri_param(string)

        __map_object_key(pair["key"], pair["value"], object)


def deserialize(string, decode_twice=True):

    """Converts a URI parameters' string into a python dictionary

    :param string: Serialized URI parameters string to deserialize
    :param decode_twice: Whether string should be decoded twice. Should be true is data was produced by this package
           and sent over the web.
    :return: Python dictionary with parsed parameters

    import urllib.parse

    #URL: http://domain/resource?name=John&age=31 or http://domain/resource?name%3DJohn%26age%3D31

    >>> string = "name=John&age=31" # or "name%3DJohn%26age%3D31"
    >>> deserialize(string)
    {'age': '31', 'name': 'John'}

    """

    parsed_data = dict()

    __deserialize(string, decode_twice, parsed_data, 0)

    return parsed_data